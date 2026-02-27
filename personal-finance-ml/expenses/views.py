from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Category, Expense, MLPredictionLog
from .serializers import CategorySerializer, ExpenseSerializer
from ml_engine.services import predict_category, detect_anomaly
from django.contrib.auth import get_user_model

User = get_user_model()

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        # We assume the user is authenticated in a real scenario
        # If not, return all or handle appropriately
        if self.request.user.is_authenticated:
            return Expense.objects.filter(user=self.request.user).order_by('-timestamp')
        return Expense.objects.all().order_by('-timestamp')

    def perform_create(self, serializer):
        # We know user is authenticated because of project settings
        user = self.request.user
            
        expense = serializer.save(user=user)

        # Non-blocking ML integration
        try:
            # Predict Category
            cat_result = predict_category(expense.description, float(expense.amount))
            category_id = cat_result.get('category_id')
            confidence = cat_result.get('confidence_score', 0.0)

            # Detect Anomaly Risk
            ano_result = detect_anomaly(expense.description, float(expense.amount))
            expense.is_anomaly = ano_result.get('is_anomaly', False)
            expense.risk_score = ano_result.get('risk_score', 0.0)

            # Assign category if we have one and user didn't explicitly pick one
            if category_id:
                try:
                    predicted_category = Category.objects.get(id=category_id)
                    if not expense.category:
                        expense.category = predicted_category
                        expense.is_ml_predicted = True
                    
                    # Log prediction
                    MLPredictionLog.objects.create(
                        expense=expense,
                        confidence_score=confidence,
                        user_overridden=(expense.category != predicted_category)
                    )
                except Category.DoesNotExist:
                    pass
            
            # Save the final mutated expense with anomaly data
            expense.save()

        except Exception as e:
            # Let it fail silently to keep it non-blocking
            pass
