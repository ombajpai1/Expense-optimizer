# PROJECT OVERVIEW

## Project Title
**ML-Driven Personal Finance & Budget Optimizer**

## Core Objective
A full-stack application that transcends standard expense tracking by acting as an AI-driven financial advisor. Its core objective is to help users reach a specific **Savings Target Range** by providing dynamically optimized expense benchmarks based directly on their **Monthly Salary** and **City Tier** (Tier 1, 2, or 3). The platform flags high-risk spending anomalies and mathematically recalculates safe category limits to ensure savings goals are actually met.

---

## User Journey
1. **Signup/Login**: Secure, JWT-authenticated entry.
2. **Input Financial Profile**: Users define their demographic baseline:
    - Monthly Salary (INR)
    - City Tier (Tier 1 = Metros, Tier 2 = Growth Hubs, Tier 3 = Small Towns)
    - Savings Goal % (e.g., "20%-30%")
3. **Add Expenses**: Users log transactions, which enter the ML pipeline. The NLP categorizer assigns tags (Rent, EMI, Food, Utilities, Education, Recreation) automatically if not selected.
4. **View Optimization Dashboard**: The Analytics page visualizes "Actual vs. AI-Recommended" spending via Clarity Charts, instantly showing users exactly where they need to cut costs to hit their savings targets.

---

## Technical Stack
### Backend
- **Framework**: Django 6.0
- **API Engine**: Django REST Framework (DRF)
- **Authentication**: Simple JWT
- **Environment**: SQLite (Local Dev), Python `.venv`

### Machine Learning Engine (Scikit-Learn)
- **NLP Categorizer**: `SGDClassifier` utilizing TF-IDF Vectorization for text-to-category processing.
- **Anomaly Detection**: Demographic-aware `IsolationForest` to flag statistically unusual transaction patterns.
- **Budget Regressor**: Multiple-output `RandomForestRegressor` trained on 10,000 vertically scaled synthetic profiles using Tier-weighted synthetic data.

### Frontend
- **Framework**: React (Vite Build System)
- **Routing**: React Router DOM (Protected Routes)
- **Icons**: Lucide-React
- **Styling**: Vanilla CSS for maximum performance, featuring custom responsive dashboards and CSS-drawn Clarity Charts.

---

## Data Schema

### User Profile (`UserProfile` Model)
Extends the native Django User model to store critical optimization parameters:
- `user` (OneToOneField)
- `monthly_salary` (DecimalField)
- `city_tier` (IntegerField: 1, 2, or 3)
- `savings_target_percentage` (IntegerField: e.g., 20)

### Expenses (`Expense` Model)
Tracks individual transactions and stores the ML pipeline's real-time analysis against it:
- `user` (ForeignKey)
- `amount` (DecimalField)
- `description` (CharField)
- `category` (ForeignKey -> Category table)
- `timestamp` (DateTimeField)
- `is_anomaly` (BooleanField) - *Flagged by IsolationForest*
- `risk_score` (FloatField) - *0.0 to 1.0 scaling factor*
- `is_ml_predicted` (BooleanField) - *True if category was auto-assigned by NLP Pipeline*

---

## ML Logic Summary

### Tier-Weighted Budgeting
The Budget Optimizer operates on an evolved version of the classic 50-30-20 rule. Instead of blankly assuming 50% for "Needs", the regressor reshapes the pie mathematically based on the **City Tier Index**.

- **Rent Weights**: A Tier 1 city user (Mumbai/Delhi) is permitted 35-40% of their salary on Rent, whereas a Tier 3 user is restricted to 10-15%. 
- **Savings Modifier**: If the user demands a 30% savings target (exceeding the baseline 20%), the algorithm forcefully shrinks the acceptable limits across scalable categories like "Recreation" and "Food" to fund the deficit.

### Regression Prediction
The backend utilizes `predict_optimized_budgets(salary, tier, savings_pct)` which feeds the user's demographic tuple into the pre-trained `RandomForestRegressor` (`budget_regressor.joblib`). This outputs exactly 6 float values representing the **Absolute Maximum INR Limit** the user is allowed to spend per category to survive the month and hit their savings goal.

---

## Feature Roadmap
- **Optimization Dashboard (Live)**: The Analytics section features month, year, and tag filters, aggressively comparing actual aggregated spend against the AI Regression limits using overlapping progressive Clarity Charts.
- **Real-Time Anomaly Detection (Live)**: Expenditures entered into the system are instantly run against an `IsolationForest`. Single transactions that are drastically over-leveraged against the user's monthly salary and tier are flagged visually as high-risk anomalies.
- **Export & Insight Generation (Upcoming)**: Allow users to download customized PDF briefs containing AI-generated strategic advice on mitigating overspend categories.
