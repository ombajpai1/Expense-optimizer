import os
import sys
import django
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Setup Django environment so we can access models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from expenses.models import Category

import random

def generate_sample_data():
    """Generate dummy data for training the model if the DB is empty."""
    print("Generating Sample Data...")
    
    # Pre-populate Categories if they don't exist
    category_names = ["Groceries", "Transport", "Entertainment", "Utilities", "Dining Out"]
    categories = {}
    for name in category_names:
        cat, _ = Category.objects.get_or_create(name=name)
        categories[name] = cat.id

    base_data = [
        {"description": "Reliance Smart", "amount": 1500.25, "category_id": categories["Groceries"]},
        {"description": "Big Bazaar", "amount": 3850.00, "category_id": categories["Groceries"]},
        {"description": "D-Mart", "amount": 2242.10, "category_id": categories["Groceries"]},
        {"description": "Uber ride to airport", "amount": 835.50, "category_id": categories["Transport"]},
        {"description": "Ola Cabs", "amount": 314.20, "category_id": categories["Transport"]},
        {"description": "Indian Oil Petrol", "amount": 2045.00, "category_id": categories["Transport"]},
        {"description": "Netflix Subscription", "amount": 649.00, "category_id": categories["Entertainment"]},
        {"description": "PVR Cinemas", "amount": 1032.50, "category_id": categories["Entertainment"]},
        {"description": "Spotify Premium", "amount": 119.00, "category_id": categories["Entertainment"]},
        {"description": "Electricity Bill", "amount": 3120.00, "category_id": categories["Utilities"]},
        {"description": "Water Utility", "amount": 445.00, "category_id": categories["Utilities"]},
        {"description": "Airtel Broadband", "amount": 980.00, "category_id": categories["Utilities"]},
        {"description": "Starbucks Coffee", "amount": 455.50, "category_id": categories["Dining Out"]},
        {"description": "McDonalds", "amount": 512.40, "category_id": categories["Dining Out"]},
        {"description": "Local Dhaba", "amount": 865.00, "category_id": categories["Dining Out"]},
    ]
    
    # Generate 1000 normal items with slight noise so the model learns a dense cluster
    normal_data = []
    for _ in range(1000):
        item = random.choice(base_data).copy()
        # Add random noise +- 20%
        item["amount"] = item["amount"] * random.uniform(0.8, 1.2)
        normal_data.append(item)

    # Inject 5 extreme anomalies (e.g. ₹80k+) that we FORCE the Isolation Forest to recognize as -1
    anomaly_data = [
        {"description": "Massive Party", "amount": 150000.00, "category_id": categories["Dining Out"]},
        {"description": "Huge Flight Tickets", "amount": 85000.00, "category_id": categories["Transport"]},
        {"description": "Insane Electronics Bill", "amount": 250000.00, "category_id": categories["Utilities"]},
        {"description": "Mega Shopping Mall", "amount": 90000.00, "category_id": categories["Groceries"]},
        {"description": "Crazy 5 Star Hotel", "amount": 120000.00, "category_id": categories["Dining Out"]},
    ]

    return pd.DataFrame(normal_data + anomaly_data)

def train_model():
    df = generate_sample_data()
    print(f"Dataset shape: {df.shape}")
    
    X = df[['description', 'amount']]
    y = df['category_id']

    # Split dataset for classifier
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 1. Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('text', TfidfVectorizer(stop_words='english', ngram_range=(1, 2)), 'description'),
            ('num', StandardScaler(), ['amount'])
        ]
    )

    # 2. Classifier Pipeline
    clf_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    print("Training Categorization Classifier...")
    clf_pipeline.fit(X_train, y_train)

    print("Evaluating Classifier...")
    y_pred = clf_pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))

    from sklearn.preprocessing import RobustScaler

    # 3. Anomaly Detection Pipeline
    # Use RobustScaler for anomalies so the massive outliers don't warp the distribution range
    anomaly_preprocessor = ColumnTransformer(
        transformers=[
            ('text', TfidfVectorizer(stop_words='english', ngram_range=(1, 2)), 'description'),
            ('num', RobustScaler(), ['amount'])
        ]
    )

    anomaly_pipeline = Pipeline(steps=[
        ('preprocessor', anomaly_preprocessor), 
        # Set contamination to 0.05
        ('isolation_forest', IsolationForest(contamination=0.05, random_state=42)) 
    ])
    
    print("Training Anomaly Detector (Isolation Forest)...")
    anomaly_pipeline.fit(X)

    # 4. Save the Models
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    clf_path = os.path.join(models_dir, 'expense_categorizer.joblib')
    anomaly_path = os.path.join(models_dir, 'anomaly_detector.joblib')
    
    joblib.dump(clf_pipeline, clf_path)
    joblib.dump(anomaly_pipeline, anomaly_path)
    print(f"Models successfully saved to {models_dir}!")

if __name__ == "__main__":
    train_model()
