import os
import joblib
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Expected to be scikit-learn pipelines
CATEGORIZER_PATH = os.path.join(settings.BASE_DIR, 'ml_engine', 'models', 'expense_categorizer.joblib')
ANOMALY_PATH = os.path.join(settings.BASE_DIR, 'ml_engine', 'models', 'anomaly_detector.joblib')

def load_models():
    """
    Loads both pre-trained models from the disk.
    """
    models = {'categorizer': None, 'anomaly': None}
    try:
        if os.path.exists(CATEGORIZER_PATH):
            models['categorizer'] = joblib.load(CATEGORIZER_PATH)
        if os.path.exists(ANOMALY_PATH):
            models['anomaly'] = joblib.load(ANOMALY_PATH)
    except Exception as e:
        logger.error(f"Failed to load ML models: {str(e)}")
    return models

# Load models globally
_loaded_models = load_models()
_cat_model = _loaded_models.get('categorizer')
_ano_model = _loaded_models.get('anomaly')

def _ensure_models_loaded():
    """Forces models to exist, allowing test frameworks to hot-reload dynamically."""
    global _cat_model, _ano_model
    if _cat_model is None or _ano_model is None:
        reloaded = load_models()
        _cat_model = reloaded.get('categorizer')
        _ano_model = reloaded.get('anomaly')

def predict_category(description: str, amount: float) -> dict:
    """Predicts expense category using the full sklearn Pipeline"""
    try:
        _ensure_models_loaded()
        if _cat_model is None:
            return {'category_id': None, 'confidence_score': 0.0}
            
        import pandas as pd
        # The model is strictly a Pipeline that expects a DataFrame with these columns
        input_data = pd.DataFrame([{'description': description, 'amount': amount}])
        
        # Pass the DataFrame straight into the Pipeline. 
        # The pipeline's 'preprocessor' step will automatically convert it using the saved TF-IDF vocabulary.
        prediction = _cat_model.predict(input_data)[0]
        probabilities = _cat_model.predict_proba(input_data)[0]
        confidence = max(probabilities)
        
        return {
            'category_id': int(prediction),
            'confidence_score': float(confidence)
        }
    except Exception as e:
        logger.error(f"Prediction failed for '{description}': {str(e)}")
        return {'category_id': None, 'confidence_score': 0.0}

def detect_anomaly(description: str, amount: float) -> dict:
    """Detects unusual spending using the full sklearn Pipeline"""
    try:
        _ensure_models_loaded()
        if _ano_model is None:
            return {'is_anomaly': False, 'risk_score': 0.0}
            
        import pandas as pd
        input_data = pd.DataFrame([{'description': description, 'amount': amount}])
        
        # Decision function returns a score (lower/negative = more abnormal)
        raw_score = float(_ano_model.decision_function(input_data)[0])
        
        # Hardcode a clearer empirical boundary for Indian Rupee scales
        # Normal INR scores end around 0.13. Anomalies like 1.5 Lakhs are ~0.10.
        is_anomaly = raw_score < 0.12
        
        # Create a dynamic risk percentage smoothly scaling from 0.14 (normal/safe) down to 0.09 (critical)
        风险 = max(0.0, min(1.0, (0.14 - raw_score) / 0.05))
        
        return {
            'is_anomaly': is_anomaly,
            'risk_score': 风险
        }
    except Exception as e:
        logger.error(f"Anomaly detection failed for '{description}': {str(e)}")
        return {'is_anomaly': False, 'risk_score': 0.0}
