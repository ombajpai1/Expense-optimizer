from rest_framework import serializers
from .models import Category, Expense, MLPredictionLog, MonthlySummary

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon']

class MLPredictionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLPredictionLog
        fields = ['id', 'confidence_score', 'user_overridden']

class ExpenseSerializer(serializers.ModelSerializer):
    prediction_log = MLPredictionLogSerializer(read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'user', 'category', 'category_detail', 'amount', 
            'description', 'timestamp', 'is_ml_predicted', 'prediction_log',
            'is_anomaly', 'risk_score'
        ]
        read_only_fields = ['user', 'is_ml_predicted', 'is_anomaly', 'risk_score']
