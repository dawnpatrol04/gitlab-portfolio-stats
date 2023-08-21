import pandas as pd
from utils.database import connect_to_db

def fetch_data_from_db(query, params=None):
    """Utility function to fetch data using pandas.read_sql."""
    df = pd.read_sql(query, connect_to_db(), params=params)
    return df

def get_num_pipeline_on_push(start_date, end_date=None):
    """Fetches the number of pipelines with source 'push' for each month between start_date and end_date."""
    end_condition = f"AND strftime('%Y-%m', created_at) <= '{end_date}'" if end_date else ""
    query = f'''SELECT strftime('%Y-%m', created_at) AS month_year, COUNT(*) AS pipeline_count
                FROM pipelines
                WHERE strftime('%Y-%m', created_at) >= '{start_date}' {end_condition} AND source = 'push'
                GROUP BY month_year
                ORDER BY month_year'''
    return fetch_data_from_db(query)

def get_num_commits(start_date, end_date=None):
    """Fetches the number of commits for each month between start_date and end_date."""
    end_condition = f"AND strftime('%Y-%m', authored_date) <= '{end_date}'" if end_date else ""
    query = f'''SELECT strftime('%Y-%m', authored_date) AS month_year, COUNT(*) AS commit_count
                FROM commits
                WHERE strftime('%Y-%m', authored_date) >= '{start_date}' {end_condition}
                GROUP BY month_year
                ORDER BY month_year'''
    return fetch_data_from_db(query)

def get_num_projects(start_date, end_date=None):
    """Fetches the number of projects created for each month between start_date and end_date."""
    end_condition = f"AND strftime('%Y-%m', created_at) <= '{end_date}'" if end_date else ""
    query = f'''SELECT strftime('%Y-%m', created_at) AS month_year, COUNT(*) AS project_count
                FROM projects
                WHERE strftime('%Y-%m', created_at) >= '{start_date}' {end_condition}
                GROUP BY month_year
                ORDER BY month_year'''
    return fetch_data_from_db(query)

def get_num_users(start_date, end_date=None):
    """Fetches the number of users added for each month between start_date and end_date."""
    end_condition = f"AND strftime('%Y-%m', created_at) <= '{end_date}'" if end_date else ""
    query = f'''SELECT strftime('%Y-%m', created_at) AS month_year, COUNT(*) AS user_count
                FROM users
                WHERE strftime('%Y-%m', created_at) >= '{start_date}' {end_condition}
                GROUP BY month_year
                ORDER BY month_year'''
    return fetch_data_from_db(query)


if __name__ == "__main__":
    # Example usage:
    print(get_num_pipeline_on_push('2019-01' ))
    print(get_num_commits('2019-01' ))
    print(get_num_projects('2019-01' ))
    print(get_num_users('2019-01' ))