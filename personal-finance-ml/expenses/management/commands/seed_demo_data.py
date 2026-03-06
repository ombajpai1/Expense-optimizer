import random
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from expenses.models import Category, Expense

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds demo data for "Tony Stark" and "Normal User" archetypes'

    def handle(self, *args, **kwargs):
        self.stdout.write("Initializing Demo Seeder...")
        # Ensure categories exist
        cats = ['Rent', 'EMI', 'Food', 'Utilities', 'Education', 'Recreation']
        for c in cats:
            Category.objects.get_or_create(name=c, defaults={'description': f'{c} expenses'})
            
        now = datetime.now()
        
        # 1. Tony Stark
        tony, created = User.objects.get_or_create(username='tony_stark', email='tony@stark.com')
        if created:
            tony.set_password('demo123')
            tony.save()
            
        tony.profile.monthly_salary = 500000
        tony.profile.city_tier = 1
        tony.profile.savings_target_percentage = 50
        tony.profile.save()
        
        self.stdout.write("Tony Stark (Tier 1, ₹5L) ready.")
        
        # 2. Normal User
        norm, created = User.objects.get_or_create(username='normal_user', email='user@demo.com')
        if created:
            norm.set_password('demo123')
            norm.save()
            
        norm.profile.monthly_salary = 60000
        norm.profile.city_tier = 2
        norm.profile.savings_target_percentage = 20
        norm.profile.save()
        
        self.stdout.write("Normal User (Tier 2, ₹60k) ready.")
        
        # Fetch Target Budgets from ML Regressor
        try:
            from ml_engine.services import predict_optimized_budgets
            tony_budgets = predict_optimized_budgets(500000, 1, 50)
            norm_budgets = predict_optimized_budgets(60000, 2, 20)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ML Engine failed to load: {str(e)}. Proceeding with hardcoded defaults."))
            # Fallbacks just in case the Random Forest joblib isn't built
            tony_budgets = {"Rent": 175000, "EMI": 50000, "Food": 15000, "Utilities": 5000, "Education": 0, "Recreation": 5000}
            norm_budgets = {"Rent": 12000, "EMI": 5000, "Food": 15000, "Utilities": 4000, "Education": 8000, "Recreation": 4000}

        def seed_expenses(user, target_budgets):
            # Clear existing expenses for the current month so we don't duplicate on multiple runs
            Expense.objects.filter(user=user, timestamp__year=now.year, timestamp__month=now.month).delete()
            
            for cat_name, budget in target_budgets.items():
                try:
                    cat = Category.objects.get(name=cat_name)
                except Category.DoesNotExist:
                    continue
                
                # To make the Clarity Chart interesting, we will strategically overspend on certain categories
                # For example, let's make them overspend on Food occasionally
                variance = random.uniform(0.85, 1.15)
                if cat_name in ['Food', 'Recreation'] and random.random() > 0.5:
                    variance = random.uniform(1.1, 1.4) # Overspend trigger!
                    
                spend = budget * variance
                if spend <= 0:
                    continue
                
                num_tx = random.randint(3, 8)
                for i in range(num_tx):
                    amount = spend / num_tx
                    Expense.objects.create(
                        user=user,
                        amount=amount,
                        description=f"Seeded {cat_name} Transaction {i+1}",
                        category=cat,
                        is_ml_predicted=True,
                        is_anomaly=(amount > (budget * 0.4)), # if a single transaction is 40% of standard monthly budget
                        risk_score=random.uniform(0.1, 0.9)
                    )
        
        seed_expenses(tony, tony_budgets)
        seed_expenses(norm, norm_budgets)
        
        self.stdout.write(self.style.SUCCESS('✨ Successfully seeded Context Demo Data! Login with tony_stark / demo123 (or normal_user / demo123) to view the live ML Analytics.'))
