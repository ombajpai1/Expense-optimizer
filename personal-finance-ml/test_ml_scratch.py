import os
import django
import sys

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from ml_engine.services import predict_optimized_budgets, predict_category

def test_profiles():
    # 1. Tier 1 High-Earner Test: Input 5,00,000 salary, Tier 1, 20% savings.
    t1 = predict_optimized_budgets(500000, 1, 20)
    print("Tier 1 (500k, 20% savings):", t1)
    
    # 2. Tier 3 Low-Earner Test: Input 30,000 salary, Tier 3, 20% savings.
    t3 = predict_optimized_budgets(30000, 3, 20)
    print("Tier 3 (30k, 20% savings):", t3)
    
    # 3. Mid-Tier with 50% Savings Goal (The "Savings Squeeze" Test)
    t2 = predict_optimized_budgets(100000, 2, 50)
    print("Tier 2 (100k, 50% savings):", t2)
    
    # NLP Test
    c1 = predict_category("Zomato Order #9982", 500)
    c2 = predict_category("Transfer to Rent A/C Jan", 15000)
    
    print("Category 'Zomato Order #9982':", c1)
    print("Category 'Transfer to Rent A/C Jan':", c2)

if __name__ == '__main__':
    test_profiles()
