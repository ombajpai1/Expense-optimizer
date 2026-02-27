from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime

from expenses.models import MonthlySummary
from .services import generate_monthly_summary

class AnalyticsViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for calculating and returning analytics data.
    """
    
    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        """
        Retrieves or generates the monthly summary for a specified year and month.
        Expected query parameters:
        - year (int)
        - month (int)
        """
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

        data = {
            "month": summary.month.strftime("%Y-%m"),
            "total_amount": float(summary.total_amount),
            "aggregated_data": summary.aggregated_data
        }

        return Response(data, status=status.HTTP_200_OK)
