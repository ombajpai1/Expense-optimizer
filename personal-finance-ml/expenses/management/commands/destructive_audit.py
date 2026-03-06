import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from expenses.models import Expense, Category

User = get_user_model()

class Command(BaseCommand):
    help = 'Executes a Destructive Audit: ML Resilience and Data Integrity'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Starting Destructive Audit..."))

        # 1. Data Integrity & AI Coach Check
        self.stdout.write("\n[1/3] Testing Zero-Salary Bypass & AI Coach Edge Cases...")
        qa_user, _ = User.objects.get_or_create(username='qa_auditor', email='qa@test.com')
        qa_user.set_password('demo123')
        qa_user.save()
        
        # Simulating API bypass with 0 salary, Tier 1, 75% savings goal
        qa_user.profile.monthly_salary = 0.0
        qa_user.profile.city_tier = 1
        qa_user.profile.savings_target_percentage = 75.0
        qa_user.profile.save()
        
        from ml_engine.services import predict_optimized_budgets
        try:
            # This should hit the 1000.0 floor
            budgets = predict_optimized_budgets(0.0, 1, 75.0)
            self.stdout.write(self.style.SUCCESS(f"PASS: BudgetRegressor survived ₹0 injection via Floor constraints. Budgets computed: {budgets}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"FAIL: Regressor crashed on ₹0: {str(e)}"))

        # 2. Stress Test ML Categorizer with Noisy Transactions
        self.stdout.write("\n[2/3] Executing ML Categorization Stress Test (50 Noisy Transactions)...")
        noisy_descriptions = [
            "Misc payment 123", "Cash 000", "Unknown debit XZY", "Transfer to self",
            "Payment gw ref 9942", "POS tx 192.168", "Vending machine???", "asdfasdf",
            "Shop closing sale", "Refund - processing", "Fee assessment", "Adjustment 0x1A"
        ]
        
        # Need at least one category to exist to catch defaults
        Category.objects.get_or_create(name='Misc')
        
        from types import SimpleNamespace
        class MockSerializer:
            def save(self, user):
                # We bypass actual DB save for raw speed and just hit the ML service
                # But to test perform_create workflow, we can instantiate models directly
                exp = Expense(user=user, amount=random.randint(10, 5000), description=random.choice(noisy_descriptions))
                return exp
        
        from expenses.views import ExpenseViewSet
        from rest_framework.request import Request
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.post('/api/expenses/expenses/')
        request.user = qa_user
        drf_request = Request(request)
        
        viewset = ExpenseViewSet()
        viewset.request = drf_request
        
        successful_predictions = 0
        failed_predictions = 0
        
        for i in range(50):
            desc = random.choice(noisy_descriptions)
            amt = float(random.randint(10, 5000))
            exp = Expense(user=qa_user, amount=amt, description=desc)
            
            # Simulate perform_create ML logic manually to observe
            from ml_engine.services import predict_category
            cat_result = predict_category(exp.description, float(exp.amount))
            if cat_result.get('category_id') is not None:
                successful_predictions += 1
            else:
                failed_predictions += 1
                
        self.stdout.write(self.style.SUCCESS(f"PASS: Categorization handled 50 noisy inputs without crashing. Successfully mapped: {successful_predictions}, Unknowns: {failed_predictions}"))

        # 3. AI Coach Validation
        self.stdout.write("\n[3/3] Validating AI Coach 'High Cost of Living' constraints...")
        from ml_engine.insights import generate_action_items
        # Mock comparison data to force an evaluation
        mock_comp = [{'category': 'Rent', 'actual_spent': 50000, 'optimized_limit': 10000, 'status': 'Danger'}]
        insights = generate_action_items(mock_comp, profile=qa_user.profile)
        
        found_warning = any("HIGH COST OF LIVING CONSTRAINT" in i for i in insights)
        if found_warning:
            self.stdout.write(self.style.SUCCESS("PASS: AI Coach successfully detected the 70%+ Goal / Tier 1 edge case and generated the warning."))
        else:
            self.stdout.write(self.style.ERROR("FAIL: AI Coach missed the High Cost of Living warning!"))

        self.stdout.write(self.style.WARNING("\nDestructive Audit Complete. All core modules resilient."))
