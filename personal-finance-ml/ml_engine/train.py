import os
import sys
import django
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_absolute_error

# Standalone ML training, completely decoupled from local database IDs
import random

def generate_sample_data():
    """Generate dummy data containing Profile Demographics and New Categories."""
    print("Generating Optimization Sample Data...")
    
    # 1. Standardized Tags (Strings only, no DB lookup)
    category_names = ["Rent", "EMI", "Food", "Utilities", "Education", "Recreation"]

    # 2. Base Data with Demographic Contexts
    # Format: description, amount, category_id, monthly_salary, city_tier
    base_data = [
        # Rent (Scales with Tier)
        {"description": "Monthly Flat Rent", "amount": 25000, "category_id": "Rent", "monthly_salary": 80000, "city_tier": 1},
        {"description": "Hostel Rent", "amount": 8000, "category_id": "Rent", "monthly_salary": 40000, "city_tier": 2},
        {"description": "Village House Rent", "amount": 3000, "category_id": "Rent", "monthly_salary": 20000, "city_tier": 3},
        
        # EMI (Scales with Salary)
        {"description": "Car Loan EMI", "amount": 15000, "category_id": "EMI", "monthly_salary": 90000, "city_tier": 1},
        {"description": "Bike EMI", "amount": 3500, "category_id": "EMI", "monthly_salary": 35000, "city_tier": 2},
        {"description": "Home Loan EMI", "amount": 35000, "category_id": "EMI", "monthly_salary": 180000, "city_tier": 1},
        
        # Food (Scales with Tier)
        {"description": "Zomato Delivery", "amount": 850, "category_id": "Food", "monthly_salary": 60000, "city_tier": 1},
        {"description": "Swiggy Order", "amount": 650, "category_id": "Food", "monthly_salary": 60000, "city_tier": 1},
        {"description": "Blinkit Groceries", "amount": 1200, "category_id": "Food", "monthly_salary": 60000, "city_tier": 1},
        {"description": "Zepto Quick Delivery", "amount": 400, "category_id": "Food", "monthly_salary": 60000, "city_tier": 1},
        {"description": "D-Mart Groceries", "amount": 4200, "category_id": "Food", "monthly_salary": 50000, "city_tier": 2},
        {"description": "Local Veg Market", "amount": 450, "category_id": "Food", "monthly_salary": 25000, "city_tier": 3},
        
        # Utilities
        {"description": "Electricity Bill", "amount": 2800, "category_id": "Utilities", "monthly_salary": 70000, "city_tier": 1},
        {"description": "Water Board Bill", "amount": 450, "category_id": "Utilities", "monthly_salary": 70000, "city_tier": 1},
        {"description": "Jio Fiber Broadband", "amount": 999, "category_id": "Utilities", "monthly_salary": 45000, "city_tier": 2},
        {"description": "Mobile Recharge Airtel", "amount": 350, "category_id": "Utilities", "monthly_salary": 20000, "city_tier": 3},
        
        # Education
        {"description": "Udemy Course", "amount": 499, "category_id": "Education", "monthly_salary": 50000, "city_tier": 2},
        {"description": "Coursera Certification", "amount": 3500, "category_id": "Education", "monthly_salary": 70000, "city_tier": 1},
        {"description": "EdX Learning", "amount": 8000, "category_id": "Education", "monthly_salary": 90000, "city_tier": 1},
        {"description": "Khan Academy Donation", "amount": 1000, "category_id": "Education", "monthly_salary": 60000, "city_tier": 2},
        {"description": "Udacity Nanodegree", "amount": 15000, "category_id": "Education", "monthly_salary": 120000, "city_tier": 1},
        {"description": "Math Tuition Fee", "amount": 2000, "category_id": "Education", "monthly_salary": 40000, "city_tier": 2},
        {"description": "College Tuition Fee", "amount": 45000, "category_id": "Education", "monthly_salary": 120000, "city_tier": 1},
        
        # Recreation
        {"description": "Netflix Premium", "amount": 649, "category_id": "Recreation", "monthly_salary": 65000, "city_tier": 1},
        {"description": "Amazon Prime Subscription", "amount": 1499, "category_id": "Recreation", "monthly_salary": 65000, "city_tier": 1},
        {"description": "PVR Movie Tickets", "amount": 950, "category_id": "Recreation", "monthly_salary": 40000, "city_tier": 2},
        {"description": "BookMyShow Event", "amount": 2500, "category_id": "Recreation", "monthly_salary": 80000, "city_tier": 1},
        {"description": "Weekend Goa Trip", "amount": 12000, "category_id": "Recreation", "monthly_salary": 85000, "city_tier": 1},
    ]

    # Generate 15000 normal transactions
    normal_data = []
    for _ in range(15000):
        item = random.choice(base_data).copy()
        item["amount"] = item["amount"] * random.uniform(0.85, 1.15) # Noise
        normal_data.append(item)

    # Inject Extreme Anomalies mapping extreme behavior relative to their contexts
    anomaly_data = [
        # Tier 3 user blowing 6 months salary on Rent
        {"description": "Luxury Villa Rent", "amount": 150000, "category_id": "Rent", "monthly_salary": 25000, "city_tier": 3},
        # Tier 2 user buying 5 iPhones 
        {"description": "Massive Electronics EMI", "amount": 350000, "category_id": "EMI", "monthly_salary": 50000, "city_tier": 2},
        # Tier 1 user dropping insane money on a single dinner
        {"description": "Insane 5 Star Hotel Party", "amount": 95000, "category_id": "Food", "monthly_salary": 100000, "city_tier": 1},
    ]

    return pd.DataFrame(normal_data + anomaly_data)


def train_model():
    df = generate_sample_data()
    print(f"Classification Dataset shape: {df.shape}")
    
    # Text Categorization (Only needs description and amount)
    X_clf = df[['description', 'amount']]
    y_clf = df['category_id'].astype(str)

    # Split dataset for classifier
    X_train, X_test, y_train, y_test = train_test_split(X_clf, y_clf, test_size=0.2, random_state=42)

    # 1. Preprocessor for Categorizer
    clf_preprocessor = ColumnTransformer(
        transformers=[
            ('text', TfidfVectorizer(stop_words='english', ngram_range=(1, 2)), 'description'),
            ('num', StandardScaler(), ['amount'])
        ]
    )

    # 2. Classifier Pipeline
    clf_pipeline = Pipeline(steps=[
        ('preprocessor', clf_preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    print("Training Categorization Classifier...")
    clf_pipeline.fit(X_train, y_train)

    print("Evaluating Classifier...")
    y_pred = clf_pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))

    from sklearn.preprocessing import RobustScaler, OneHotEncoder

    # Anomaly Detection (Needs deep context: amount, salary, tier)
    X_ano = df[['description', 'amount', 'monthly_salary', 'city_tier']]
    
    # 3. Anomaly Detection Pipeline (Factoring in Salary & Tier)
    anomaly_preprocessor = ColumnTransformer(
        transformers=[
            ('text', TfidfVectorizer(stop_words='english', ngram_range=(1, 2)), 'description'),
            ('num_robust', RobustScaler(), ['amount', 'monthly_salary']),
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['city_tier'])
        ]
    )

    anomaly_pipeline = Pipeline(steps=[
        ('preprocessor', anomaly_preprocessor), 
        ('isolation_forest', IsolationForest(contamination=0.05, random_state=42)) 
    ])
    
    print("Training Demographic Anomaly Detector (Isolation Forest)...")
    anomaly_pipeline.fit(X_ano)


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
