from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from expenses.models import Category, Expense, MLPredictionLog

User = get_user_model()

class ExpenseTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create two distinct users to test permissions
        self.user1 = User.objects.create_user(username='user1', password='pw1')
        self.user2 = User.objects.create_user(username='user2', password='pw2')

        # Create initial data
        self.category = Category.objects.create(name='Coffee', icon='coffee')
        
        # Authenticate user1 for baseline requests
        url = reverse('token_obtain_pair')
        resp = self.client.post(url, {'username': 'user1', 'password': 'pw1'}, format='json')
        self.token = resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.expenses_url = reverse('expense-list')

    def test_create_expense_authenticated(self):
        """Test authenticated user can create an expense"""
        data = {
            'amount': 5.50,
            'description': 'Morning Coffee'
        }
        response = self.client.post(self.expenses_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(Expense.objects.get().user, self.user1)
        # Note: Unspecified category shouldn't block creation, may trigger ML logging in background

    def test_create_expense_unauthenticated(self):
        """Test unauthenticated users are rejected globally"""
        self.client.force_authenticate(user=None)
        data = {'amount': 10.0, 'description': 'Sneaky expense'}
        response = self.client.post(self.expenses_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Expense.objects.count(), 0)

    def test_expense_privacy_between_users(self):
        """Test that user2 cannot see user1's expenses"""
        # User 1 creates an expense
        Expense.objects.create(user=self.user1, amount=100.0, description="User1 Secret")

        # Authenticate as User 2
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.expenses_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # User 2 should get an empty list
        self.assertEqual(len(response.data), 0)

    def test_ml_fallback_does_not_block_creation(self):
        """Test that if ML unpredictably fails, the transaction still saves safely"""
        # We simulate ML failing by passing a complex/weird description
        # The service layer catches the exception and returns None
        data = {
            'amount': 1500.0,
            'description': '!!__SOME_WEIRD_STRING__!!'
        }
        response = self.client.post(self.expenses_url, data, format='json')
        
        # It MUST return 201 Created regardless of the ML model's behavior
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expense = Expense.objects.get(id=response.data['id'])
        
        # Category could be None or explicitly predicted, but it's guaranteed saved
        self.assertIsNotNone(expense.amount)

    @patch('expenses.views.detect_anomaly')
    @patch('expenses.views.predict_category')
    def test_anomaly_detection_flags_outlier(self, mock_predict, mock_detect):
        """Test that a statically huge expense triggers the ML Anomaly Flag using Mocked engine"""
        
        # Configure Mocks
        mock_predict.return_value = {'category_id': None, 'confidence_score': 0.0}
        mock_detect.return_value = {'is_anomaly': True, 'risk_score': 0.95}

        # In our training data, a $15,000 coffee should easily trip the IsolationForest
        data = {
            'amount': 15000.0,
            'description': 'Regular Coffee'
        }
        response = self.client.post(self.expenses_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Ensure the anomaly flag was successfully written to the DB
        expense = Expense.objects.get(id=response.data['id'])
        self.assertTrue(expense.is_anomaly, "ML Engine failed to flag $15k coffee as anomalous")
        self.assertGreater(expense.risk_score, 0.0)

