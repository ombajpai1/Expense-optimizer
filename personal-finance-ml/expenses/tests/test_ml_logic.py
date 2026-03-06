from django.test import TestCase
from ml_engine.services import predict_optimized_budgets, predict_category
from expenses.models import Category

class MLLogicTests(TestCase):
    def setUp(self):
        category_names = ["Rent", "EMI", "Food", "Utilities", "Education", "Recreation"]
        for name in category_names:
            Category.objects.create(name=name)
        
        self.food_cat = Category.objects.get(name="Food")
        self.rent_cat = Category.objects.get(name="Rent")

    def test_tier1_high_earner(self):
        # Prompt: Input 5,00,000 salary, Tier 1. Verify Rent limit is ~ 1,75,000 - 2,00,000 (35-40%).
        budget = predict_optimized_budgets(500000, 1, 20)
        rent = budget.get('Rent', 0)
        # The Regressor now trains up to 10L, so 5L is safely inside bounds and will correctly predict
        self.assertTrue(175000 <= rent <= 200000, f"Failed: Rent {rent} is outside the 1.75L - 2.0L boundary.")

    def test_tier3_low_earner(self):
        # Prompt: Input 30,000 salary, Tier 3. Verify Rent limit is ~ 3,000 - 4,500 (10-15%).
        budget = predict_optimized_budgets(30000, 3, 20)
        rent = budget.get('Rent', 0)
        self.assertTrue(3000 <= rent <= 4500, f"Failed: Rent {rent} is outside 3k-4.5k boundary.")

    def test_savings_squeeze(self):
        # Prompt: Input a 50% savings goal. Verify that the "Recreation" budget is forced to 0.
        budget = predict_optimized_budgets(100000, 2, 50)
        recreation = budget.get('Recreation', 100)
        self.assertEqual(recreation, 0.0, f"Failed: Recreation {recreation} was not mathematically squeezed to 0.")

    def test_nlp_categorization_zomato(self):
        # Input: "Zomato Order #9982" -> Expected: Dining/Food
        cat = predict_category("Zomato Order #9982", 500)
        self.assertEqual(cat['category_id'], self.food_cat.id, f"Predicted {cat['category_id']} instead of Food")

    def test_nlp_categorization_rent(self):
        # Input: "Transfer to Rent A/C Jan" -> Expected: Rent
        cat = predict_category("Transfer to Rent A/C Jan", 15000)
        self.assertEqual(cat['category_id'], self.rent_cat.id, f"Predicted {cat['category_id']} instead of Rent")
