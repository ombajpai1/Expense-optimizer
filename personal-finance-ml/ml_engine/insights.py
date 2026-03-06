def generate_action_items(comparison_data, **kwargs):
    """
    Analyzes the comparison data (actual vs. optimized limit) 
    and generates 3-5 strategic action items for the user.
    
    comparsion_data format expected:
    [
        {
            "category": "Rent", 
            "actual_spent": 40000, 
            "optimized_limit": 35000, 
            "status": "Danger"
        },
        ...
    ]
    """
    profile = kwargs.get('profile', None)
    
    if not comparison_data:
        return ["No expense data available to analyze this month."]

    # Calculate deviations
    deviations = []
    for item in comparison_data:
        actual = item.get('actual_spent', 0)
        limit = item.get('optimized_limit', 0)
        
        overspend_amount = actual - limit
        # Add to deviations if overspent
        if overspend_amount > 0:
            deviations.append({
                'category': item.get('category'),
                'overspend': overspend_amount,
                'pct_over': (overspend_amount / limit * 100) if limit > 0 else 100
            })

    # Sort sequentially by greatest absolute overspend
    deviations.sort(key=lambda x: x['overspend'], reverse=True)

    action_items = []

    if not deviations:
        action_items.append("Excellent work! You are currently operating under all AI-optimized target limits.")
        action_items.append("Consider re-allocating any surplus funds directly into investments or a high-yield savings account.")
        return action_items
        
    # AI Coach Edge Case: High Cost of Living Constraints (Tier 1 + >= 70% Goal)
    if profile:
        try:
            tier = int(getattr(profile, 'city_tier', 2))
            goal = float(getattr(profile, 'savings_target_percentage', 20.0))
            if tier == 1 and goal >= 70.0:
                action_items.append("⚠️ HIGH COST OF LIVING CONSTRAINT: You have set a massive 70%+ savings goal while living in a Tier 1 Metro. This forces extreme Regressor limits. Re-evaluate if this goal is statistically viable without suffering lifestyle burnout.")
        except Exception:
            pass

    # 1. Primary Offender
    primary = deviations[0]
    action_items.append(
        f"Critical Focus: Your '{primary['category']}' spending is ₹{primary['overspend']:,.2f} over the mathematical benchmark. "
        f"Reducing this single category will yield the highest impact on your savings target."
    )

    # 2. Secondary Offender (if exists)
    if len(deviations) > 1:
        secondary = deviations[1]
        action_items.append(
            f"Secondary Drain: Look into optimizing your '{secondary['category']}' costs. "
            f"You are exceeding the ML tier limit by {secondary['pct_over']:.1f}%. Ask yourself if these are 'needs' or 'wants'."
        )

    # 3. Micro-Optimization (if there's a 3rd)
    if len(deviations) > 2:
        tertiary = deviations[2]
        action_items.append(
            f"Micro-Optimization: Curbing '{tertiary['category']}' by just ₹{tertiary['overspend']:,.2f} brings you back to safety."
        )

    # 4. Aggregate warning 
    total_overspend = sum(d['overspend'] for d in deviations)
    action_items.append(
        f"Overall Impact: Across {len(deviations)} over-budget categories, you are leaking ₹{total_overspend:,.2f} "
        "that should be going towards your primary Savings Target."
    )

    return action_items
