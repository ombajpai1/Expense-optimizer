def calculate_optimized_budget(monthly_salary: float, city_tier: int) -> dict:
    """
    Calculates dynamic Target Budgets (Benchmarking limits) for each ML Category
    based on the user's demographic inputs.

    Returns a dictionary of Category names and their localized maximum INR budget limit.
    """
    salary = float(monthly_salary)
    
    # 1. Base Budget Ratios (e.g., 50/30/20 Rule adjustments)
    # These represent the core percentage of income allocated to functional areas.
    allocations = {
        "Rent": 0.30,       # 30% baseline
        "EMI": 0.15,        # 15% debt
        "Food": 0.15,       # 15% living
        "Utilities": 0.05,  # 5% living
        "Education": 0.10,  # 10% growth
        "Recreation": 0.05, # 5% fun
    }

    # 2. Demographic Multipliers based on City Tier
    # Tier 1 cities cost more for rent, but salaries ostensibly scale to match.
    # However, ratios explicitly shift based on the living baseline.
    if city_tier == 1:
        allocations["Rent"] += 0.10      # Tier 1 rent is aggressively higher (40%)
        allocations["Food"] += 0.05      # Tier 1 groceries/delivery are higher (20%)
        # Compensate by reducing EMI float
        allocations["EMI"] -= 0.05
    elif city_tier == 3:
        allocations["Rent"] -= 0.10      # Tier 3 rent is incredibly cheap (20%)
        allocations["Food"] -= 0.05      # Tier 3 local groceries are cheaper (10%)
        
    # 3. Calculate Hard Constraints
    target_budgets = {}
    total_allocated = 0.0
    
    for category, ratio in allocations.items():
        budget = salary * ratio
        target_budgets[category] = budget
        total_allocated += budget
        
    # Standardize the output
    return target_budgets

def evaluate_spending(optimized_budgets: dict, actual_spending_aggregate: dict) -> dict:
    """
    Compares the calculated optimal benchmarks against the user's LIVE actual spending habits
    for the current month to flag over/under optimization.
    """
    results = {}
    for category, limit in optimized_budgets.items():
        actual = actual_spending_aggregate.get(category, 0.0)
        percentage_used = (actual / limit) * 100 if limit > 0 else 0
        
        status = "Optimal"
        if percentage_used > 100:
            status = "Over Budget"
        elif percentage_used < 75:
            status = "Under Budget (Saving)"
            
        results[category] = {
            "target_limit": limit,
            "actual_spent": actual,
            "percentage_used": percentage_used,
            "status": status,
            "variance": limit - actual
        }
        
    return results
