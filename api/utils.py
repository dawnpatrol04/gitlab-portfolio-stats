def get_users_count_per_month(users):
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=6*30)  # Approximation for 6 months
    
    # Filter users added within the desired date range
    recent_users = [user for user in users if start_date <= user.created_at <= end_date]
    
    monthly_counts = {}
    for user in recent_users:
        month_year = user.created_at.strftime('%B %Y')
        if month_year in monthly_counts:
            monthly_counts[month_year] += 1
        else:
            monthly_counts[month_year] = 1

    # Ensure we have counts for all months even if they are 0
    for month_offset in range(6, -1, -1):
        month_year = (end_date - timedelta(days=30*month_offset)).strftime('%B %Y')
        if month_year not in monthly_counts:
            monthly_counts[month_year] = 0

    return monthly_counts