import os
import sys
import pandas as pd
import joblib
import random
import django

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# Add the project root to the sys path so Django settings can be loaded
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

def calculate_optimal_budget(salary, city_tier, savings_target_pct):
    """
    Tier-Weighted Budgeting using the 50-30-20 Rule adapted for City Tiers.
    Tier 1 user gets 35-40% Rent, Tier 3 user gets 10-15% Rent.
    """
    # Base weights by Tier
    weights = {
        1: {'Rent': 0.35, 'Food': 0.12, 'Utilities': 0.05, 'EMI': 0.10, 'Education': 0.08},
        2: {'Rent': 0.22, 'Food': 0.15, 'Utilities': 0.05, 'EMI': 0.08, 'Education': 0.10},
        3: {'Rent': 0.12, 'Food': 0.18, 'Utilities': 0.07, 'EMI': 0.05, 'Education': 0.10}
    }
    
    selected_weight = weights.get(city_tier, weights[2])
    
    # Calculate initial needs
    optimized_spending = {cat: salary * w for cat, w in selected_weight.items()}
    total_needs = sum(optimized_spending.values())
    
    # Calculate available for 'Wants' (Recreation) after the User's specific Savings Target
    savings_amount = salary * (savings_target_pct / 100)
    recreation_fund = salary - total_needs - savings_amount
    
    # If savings target is too high, recreation shrinks to fund it
    optimized_spending['Recreation'] = max(0, recreation_fund)
    
    return optimized_spending


def generate_budget_training_data(num_samples=15000):
    """Generate 15000 demographic combinations to train the target limits."""
    print(f"Generating {num_samples} Sample Base Synthetics ...")
    data = []
    
    categories = ["Rent", "EMI", "Food", "Utilities", "Education", "Recreation"]
    
    for _ in range(num_samples):
        # Generate realistic random demographics spanning Extreme boundaries
        salary = random.randint(5000, 1000000)
        tier = random.choice([1, 2, 3])
        savings_target = random.choice([10, 20, 25, 30, 40])
        
        # Calculate the mathematical optimal budget limit according to Tier Rules
        optimal = calculate_optimal_budget(salary, tier, savings_target)
        
        row = {
            'monthly_salary': salary,
            'city_tier': tier,
            'savings_target_pct': savings_target,
        }
        
        for cat in categories:
            row[f"target_{cat}"] = optimal.get(cat, 0.0)
            
        data.append(row)
        
    return pd.DataFrame(data)


def train_regressor():
    budget_df = generate_budget_training_data()
    print(f"Regression Dataset shape Compiled: {budget_df.shape}")
    
    # Input features
    X = budget_df[['monthly_salary', 'city_tier', 'savings_target_pct']]
    
    # Targets
    target_columns = [col for col in budget_df.columns if col.startswith('target_')]
    y = budget_df[target_columns]
    
    # Data preprocessing logic
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), ['monthly_salary', 'savings_target_pct']),
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['city_tier'])
        ]
    )
    
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    print("Training Phase 2 ML Target Budget Regressor...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    pipeline.fit(X_train, y_train)
    
    # Validate Accuracy
    print("Evaluating Budget Predictive Model...")
    y_pred = pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Mean Absolute Alignment Deviation: {mae:.2f} INR")

    # Serialize & Dump Model
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    budget_path = os.path.join(models_dir, 'budget_regressor.joblib')
    joblib.dump(pipeline, budget_path)
    print(f"Successfully saved {budget_path}!")

if __name__ == '__main__':
    train_regressor()
