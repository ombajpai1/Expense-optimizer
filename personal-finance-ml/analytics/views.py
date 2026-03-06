from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from expenses.models import MonthlySummary
from .services import generate_monthly_summary

class AnalyticsViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for calculating and returning analytics data.
    """
    
    @extend_schema(
        summary="Get Monthly Budget Analytics",
        description="Retrieves a summarized view of expenditures vs ML Budgets. Expected format includes target_budgets and spending_evaluation scores for the frontend progress bars.",
        parameters=[
            OpenApiParameter(name='year', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='Target Year', required=False),
            OpenApiParameter(name='month', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='Target Month', required=False)
        ]
    )
    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        user = request.user if request.user.is_authenticated else None
        if not user:
            from django.contrib.auth import get_user_model
            user = get_user_model().objects.first()
            if not user:
                 return Response({"error": "No users found."}, status=status.HTTP_400_BAD_REQUEST)

        year = request.query_params.get('year')
        month = request.query_params.get('month')

        now = datetime.now()
        if not year or not month:
            # Fallback to current year/month
            year = now.year
            month = now.month

        try:
            year, month = int(year), int(month)
        except ValueError:
            return Response({"error": "Invalid year or month format"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate or retrieve the summary
        summary = generate_monthly_summary(user, year, month)

        from ml_engine.services import predict_optimized_budgets
        from ml_engine.optimization import evaluate_spending
        
        # Calculate dynamic limits using User Profile and ML Regressor
        salary = 0.0
        tier = 2
        savings_str = '20'
        
        try:
            profile = user.profile
            salary = float(getattr(profile, 'monthly_salary', 0.0))
            tier = int(getattr(profile, 'city_tier', 2))
            savings_pct = float(getattr(profile, 'savings_target_percentage', 20))
        except Exception:
            savings_pct = 20.0
        
        optimized_budgets = predict_optimized_budgets(salary, tier, savings_pct)
        spending_evaluation = evaluate_spending(optimized_budgets, summary.aggregated_data)

        data = {
            "month": summary.month.strftime("%Y-%m"),
            "total_amount": float(summary.total_amount),
            "aggregated_data": summary.aggregated_data,
            "optimization": {
                "target_budgets": optimized_budgets,
                "evaluation": spending_evaluation,
                "monthly_salary": salary,
                "city_tier": tier,
                "savings_target_pct": savings_pct
            }
        }

        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Download AI Monthly PDF",
        description="Generates a formatted PDF on the fly using reportlab. Includes the Total Spend, Salary, Savings Goal, AI Strategy List, and an embedded Clarity Chart table comparing Actual vs Optimized budgets.",
        parameters=[
            OpenApiParameter(name='year', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='Target Year', required=False),
            OpenApiParameter(name='month', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='Target Month', required=False)
        ]
    )
    @action(detail=False, methods=['get'], url_path='download-report')
    def download_report(self, request):
        user = request.user if request.user.is_authenticated else None
        if not user:
            from django.contrib.auth import get_user_model
            user = get_user_model().objects.first()
            if not user:
                 return Response({"error": "No users found."}, status=status.HTTP_400_BAD_REQUEST)

        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        from datetime import datetime
        now = datetime.now()
        try:
            year = int(year) if year else now.year
            month = int(month) if month else now.month
        except ValueError:
            return Response({"error": "Invalid year or month format"}, status=status.HTTP_400_BAD_REQUEST)

        # Mirror comparison stats logic
        from django.db.models import Sum
        from expenses.models import Expense, Category
        expenses = Expense.objects.filter(
            user=user,
            timestamp__year=year,
            timestamp__month=month,
            category__isnull=False
        ).values('category__name').annotate(total=Sum('amount'))
        
        actual_spend = {item['category__name']: float(item['total']) for item in expenses}
        
        from ml_engine.services import get_optimized_budget
        target_limits = get_optimized_budget(user.profile) if hasattr(user, 'profile') else {}
        
        categories = Category.objects.values_list('name', flat=True)
        comparison = []
        for cat in categories:
            actual = actual_spend.get(cat, 0.0)
            optimized = target_limits.get(cat, 0.0)
            comparison.append({
                'category': cat,
                'actual_spent': actual,
                'optimized_limit': optimized,
                'status': 'Danger' if actual > optimized else 'Safe'
            })
            
        monthly_salary = float(user.profile.monthly_salary) if hasattr(user, 'profile') else 0.0
        total_spent = sum(actual_spend.values())
        current_savings = max(0.0, monthly_salary - total_spent)

        # Generate Action Items
        from ml_engine.insights import generate_action_items
        action_items = generate_action_items(comparison, profile=getattr(user, 'profile', None))

        # Generate PDF
        from django.http import FileResponse
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        import io

        buffer = io.BytesIO()

        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 750, f"AI Monthly Analytics Report ({year}-{month:02d})")

        p.setFont("Helvetica", 12)
        p.drawString(50, 720, f"Total Monthly Spend: INR {total_spent:,.2f}")
        p.drawString(50, 700, f"Monthly Salary: INR {monthly_salary:,.2f} | Savings Status: INR {current_savings:,.2f}")
        
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, 660, "Strategic AI Action Items:")
        
        y_pos = 630
        p.setFont("Helvetica", 11)
        for item in action_items:
            import textwrap
            lines = textwrap.wrap(item, width=95)
            for line in lines:
                p.drawString(60, y_pos, f"- {line}")
                y_pos -= 20
            y_pos -= 10
        
        y_pos -= 20
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y_pos, "Clarity Breakdown (Actual vs Target):")
        y_pos -= 30

        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y_pos, "Category")
        p.drawString(200, y_pos, "Actual Spend")
        p.drawString(320, y_pos, "Optimized Limit")
        p.drawString(450, y_pos, "Status")
        y_pos -= 20
        p.setFont("Helvetica", 10)

        for comp in comparison:
            p.drawString(50, y_pos, comp['category'])
            p.drawString(200, y_pos, f"INR {comp['actual_spent']:,.2f}")
            p.drawString(320, y_pos, f"INR {comp['optimized_limit']:,.2f}")
            
            p.setFillColor(colors.red if comp['status'] == 'Danger' else colors.green)
            p.drawString(450, y_pos, comp['status'])
            p.setFillColor(colors.black)
            
            y_pos -= 20
            if y_pos < 50:
                p.showPage()
                p.setFont("Helvetica", 10)
                y_pos = 750

        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"Financial_Report_{month:02d}_{year}.pdf", content_type='application/pdf')
