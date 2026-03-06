from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from expenses.models import Category, Expense

User = get_user_model()

class AnomalyAPITests(APITestCase):
    def setUp(self):
        # 1. Setup user with 20k salary
        self.user = User.objects.create_user(username='anomalyuser', password='password123')
        self.user.profile.monthly_salary = 20000
        self.user.profile.city_tier = 3
        self.user.profile.savings_target_percentage = 20
        self.user.profile.save()
        
        # 2. Setup categories
        category_names = ["Rent", "EMI", "Food", "Utilities", "Education", "Recreation"]
        for name in category_names:
            Category.objects.create(name=name)
            
        self.cat = Category.objects.get(name='Recreation')
        
    def test_post_anomalous_expense(self):
        # 3. Setup client & authenticate
        self.client.force_authenticate(user=self.user)
        
        # 4. Post extreme expense
        payload = {
            'amount': 100000,
            'description': 'Luxury Watch',
            'category': self.cat.id
        }
        url = '/api/expenses/expenses/'
        response = self.client.post(url, payload, format='json')
        
        # 5. Assert API Success
        self.assertEqual(response.status_code, 201)
        
        # 6. Fetch the created expense
        data = response.json()
        expense = Expense.objects.get(id=data['id'])
        
        # 7. Assert ML flagged it properly
        self.assertTrue(expense.is_anomaly, "Expense should be flagged as an anomaly.")
        self.assertGreater(expense.risk_score, 0.9, f"Risk score ({expense.risk_score}) should be > 0.9.")
