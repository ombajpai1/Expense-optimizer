import os
import joblib
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Expected to be scikit-learn pipelines
import os
# __file__ is ml_engine/services.py, so dirname is ml_engine
ML_ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
CATEGORIZER_PATH = os.path.join(ML_ENGINE_DIR, 'models', 'expense_categorizer.joblib')
ANOMALY_PATH = os.path.join(ML_ENGINE_DIR, 'models', 'anomaly_detector.joblib')
BUDGET_PATH = os.path.join(ML_ENGINE_DIR, 'models', 'budget_regressor.joblib')

def load_models():
    """
    Loads pre-trained models from the disk.
    """
    models = {'categorizer': None, 'anomaly': None, 'budget': None}
    try:
        if os.path.exists(CATEGORIZER_PATH):
            models['categorizer'] = joblib.load(CATEGORIZER_PATH)
        if os.path.exists(ANOMALY_PATH):
            models['anomaly'] = joblib.load(ANOMALY_PATH)
        if os.path.exists(BUDGET_PATH):
            models['budget'] = joblib.load(BUDGET_PATH)
    except Exception as e:
        logger.error(f"Failed to load ML models: {str(e)}")
    return models

# Load models globally
_loaded_models = load_models()
_cat_model = _loaded_models.get('categorizer')
_ano_model = _loaded_models.get('anomaly')
_budget_model = _loaded_models.get('budget')

def _ensure_models_loaded():
    """Forces models to exist, allowing test frameworks to hot-reload dynamically."""
    global _cat_model, _ano_model, _budget_model
    if _cat_model is None or _ano_model is None or _budget_model is None:
        reloaded = load_models()
        _cat_model = reloaded.get('categorizer')
        _ano_model = reloaded.get('anomaly')
        _budget_model = reloaded.get('budget')

def predict_category(description: str, amount: float) -> dict:
    """Predicts expense category using the full sklearn Pipeline"""
    try:
        _ensure_models_loaded()
        if _cat_model is None:
            return {'category_id': None, 'confidence_score': 0.0}
            
        import pandas as pd
        import re
        
        # Text Normalization
        normalized_desc = re.sub(r'[^a-z0-9\s]', '', str(description).lower())
        
        input_data = pd.DataFrame([{'description': normalized_desc, 'amount': amount}])
        
        prediction = _cat_model.predict(input_data)[0]
        probabilities = _cat_model.predict_proba(input_data)[0]
        confidence = max(probabilities)
        
        from expenses.models import Category
        # The model directly predicts the exact STRING ("Food")
        predicted_name = str(prediction).strip()
        
        try:
            # Dynamically fetch the actual DB ID for whatever environment this runs in
            logger.info(f"Looking up Category String Match exactly: '{predicted_name}'")
            category_db = Category.objects.get(name__iexact=predicted_name)
            cat_id = category_db.id
        except Category.DoesNotExist:
            cat_id = None
            
        return {
            'category_id': cat_id,
            'confidence_score': float(confidence)
        }
    except Exception as e:
        logger.error(f"Prediction failed for '{description}': {str(e)}")
        return {'category_id': None, 'confidence_score': 0.0}

def detect_anomaly(expense) -> dict:
    """Detects unusual spending using ML and flags if category budget is exceeded."""
    try:
        _ensure_models_loaded()
        if _ano_model is None:
            return {'is_anomaly': False, 'risk_score': 0.0}
            
        try:
            profile = expense.user.profile
            monthly_salary = float(profile.monthly_salary)
            city_tier = int(profile.city_tier)
        except Exception:
            monthly_salary = 0.0
            city_tier = 2
            
        import pandas as pd
        input_data = pd.DataFrame([{
            'description': expense.description, 
            'amount': float(expense.amount),
            'monthly_salary': monthly_salary,
            'city_tier': city_tier
        }])
        
        raw_score = float(_ano_model.decision_function(input_data)[0])
        is_ml_anomaly = raw_score < 0.10
        risk = max(0.0, min(1.0, (0.13 - raw_score) / 0.08))
        
        # Check Optimized Limit bounds
        is_budget_anomaly = False
        if expense.category and hasattr(expense.user, 'profile'):
            from expenses.models import Expense
            from django.utils import timezone
            from django.db.models import Sum
            
            now = timezone.now()
            # current_spent includes this expense since it was already saved
            current_spent = Expense.objects.filter(
                user=expense.user,
                category=expense.category,
                timestamp__year=now.year,
                timestamp__month=now.month
            ).aggregate(total=Sum('amount'))['total'] or 0.0
            
            budgets = get_optimized_budget(expense.user.profile)
            target_limit = budgets.get(expense.category.name, float('inf'))
            
            if float(current_spent) > target_limit:
                is_budget_anomaly = True
                # Anomaly Calibration: The user requested a non-linear boost for massive ratio breaks
                excess_ratio = float(current_spent) / monthly_salary if monthly_salary > 0 else 1.0
                if excess_ratio > 1.0:
                    # Exponential break - spend > salary
                    risk = min(1.0, 0.85 + (excess_ratio * 0.15))
                else:
                    risk = max(risk, 0.85)  # Boost risk heavily if budget breached
        
        return {
            'is_anomaly': is_ml_anomaly or is_budget_anomaly,
            'risk_score': risk
        }
    except Exception as e:
        logger.error(f"Anomaly detection failed for '{expense.id}': {str(e)}")
        return {'is_anomaly': False, 'risk_score': 0.0}

def get_optimized_budget(user_profile) -> dict:
    """Fetches Target Limits as a JSON dict for the specified User Profile."""
    try:
        salary = float(getattr(user_profile, 'monthly_salary', 0.0))
        tier = int(getattr(user_profile, 'city_tier', 2))
        savings_pct = float(getattr(user_profile, 'savings_target_percentage', 20))
        return predict_optimized_budgets(salary, tier, savings_pct)
    except Exception as e:
        logger.error(f"Failed to get optimized budget: {e}")
        return {}

def predict_optimized_budgets(monthly_salary: float, city_tier: int, savings_target_pct: float) -> dict:
    """
    Predicts the Category Target Limits directly from the ML Regressor.
    """
    import pandas as pd
    
    # Fallback to deterministic logic if model cannot load
    try:
        _ensure_models_loaded()
        if _budget_model is None:
            raise ValueError("Model missing")
            
        # Data Integrity QA: Impose a mathematical floor to prevent malicious ₹0 API injections from breaking the Budget Regressor logic.
        safe_salary = max(1000.0, float(monthly_salary))
        
        input_data = pd.DataFrame([{
            'monthly_salary': safe_salary,
            'city_tier': int(city_tier),
            'savings_target_pct': float(savings_target_pct)
        }])
        
        predictions = _budget_model.predict(input_data)[0]
        
        # Manually map the prediction output arrays back into strings
        categories = ["Rent", "EMI", "Food", "Utilities", "Education", "Recreation"]
        
        budgets = {}
        for idx, cat in enumerate(categories):
            # Ensure no negative budgets map out of the regressor
            budgets[cat] = max(0.0, float(predictions[idx]))
            
        return budgets
    except Exception as e:
        logger.error(f"Budget regression failed: {str(e)}. Falling back to deterministic calculating logic.")
        from ml_engine.optimization import calculate_optimized_budget
        return calculate_optimized_budget(monthly_salary, city_tier)
