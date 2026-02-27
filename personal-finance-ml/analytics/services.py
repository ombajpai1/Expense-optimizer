import datetime
from django.db.models import Sum
from expenses.models import Expense, MonthlySummary, Category

def generate_monthly_summary(user, year: int, month: int):
    """
    Calculates and saves the monthly summary for a given user and month.
    """
    # Start date of the month
    start_date = datetime.date(year, month, 1)
    
    # End date of the month (handle December logic)
    if month == 12:
        end_date = datetime.date(year + 1, 1, 1)
    else:
        end_date = datetime.date(year, month + 1, 1)

    # Filter expenses
    expenses = Expense.objects.filter(
        user=user,
        timestamp__date__gte=start_date,
        timestamp__date__lt=end_date
    )

    total_amount = expenses.aggregate(total=Sum('amount'))['total'] or 0.0

    # Aggregate by category
    aggregated_data = {}
    for expense in expenses:
        cat_name = expense.category.name if expense.category else "Uncategorized"
        aggregated_data[cat_name] = aggregated_data.get(cat_name, 0.0) + float(expense.amount)

    # Update or create the MonthlySummary record
    summary, created = MonthlySummary.objects.update_or_create(
        user=user,
        month=start_date,
        defaults={
            'total_amount': total_amount,
            'aggregated_data': aggregated_data
        }
    )

    return summary
