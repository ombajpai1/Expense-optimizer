from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Used for ML Budget Optimization")
    CITY_TIERS = (
        (1, 'Tier 1 (Metro)'),
        (2, 'Tier 2 (Urban)'),
        (3, 'Tier 3 (Semi-Urban/Rural)'),
    )
    city_tier = models.IntegerField(choices=CITY_TIERS, default=2)
    savings_target_percentage = models.IntegerField(default=20, help_text="e.g. 25 for 25%")

    def __str__(self):
        return f"{self.user.username} Profile"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Icon name or URL")

    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='expenses')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_ml_predicted = models.BooleanField(default=False)
    is_anomaly = models.BooleanField(default=False, help_text="Flagged by ML as unusual spending")
    risk_score = models.FloatField(default=0.0, help_text="Anomaly confidence/risk score (0 to 1)")
    needs_review = models.BooleanField(default=False, help_text="Set to True if ML confidence is low < 0.75")

    def __str__(self):
        return f"{self.user} - {self.amount} - {self.description[:20]}"

class MLPredictionLog(models.Model):
    expense = models.OneToOneField(Expense, on_delete=models.CASCADE, related_name='prediction_log')
    confidence_score = models.FloatField()
    user_overridden = models.BooleanField(default=False)

    def __str__(self):
        return f"Log for {self.expense.id} - Score: {self.confidence_score}"

class MonthlySummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='monthly_summaries')
    month = models.DateField(help_text="First day of the month")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    aggregated_data = models.JSONField(default=dict, help_text="Category-wise breakdown or similar data")

    def __str__(self):
        return f"{self.user} - {self.month.strftime('%Y-%m')} - {self.total_amount}"
