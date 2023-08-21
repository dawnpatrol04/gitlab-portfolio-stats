import pandas as pd
from datetime import datetime
import json


from utils.database import connect_to_db
from src.value.dynamic_values  import get_num_pipeline_on_push, get_num_commits, get_num_projects, get_num_users
# from imput_validaton import read_json_file, validate_data



def fetch_data_from_db(query, params=None):
    """Utility function to fetch data using pandas.read_sql."""
    df = pd.read_sql(query, connect_to_db(), params=params)
    return df



def fetch_dynamic_values_for_date_range(start_date, end_date=None):
    """Fetches dynamic values from the database for a given date range."""
    dynamic_values = {}
    
    # Get number of pipelines with source 'push'
    pipelines_df = get_num_pipeline_on_push(start_date, end_date)
    if not pipelines_df.empty:
        dynamic_values['num_pipeline_on_push'] = pipelines_df['pipeline_count'].sum()
    
    # Get number of commits
    commits_df = get_num_commits(start_date, end_date)
    if not commits_df.empty:
        dynamic_values['num_commits'] = commits_df['commit_count'].sum()

    # Get number of projects created
    projects_df = get_num_projects(start_date, end_date)
    if not projects_df.empty:
        dynamic_values['num_projects'] = projects_df['project_count'].sum()

    # Get number of users added
    users_df = get_num_users(start_date, end_date)
    if not users_df.empty:
        dynamic_values['num_users'] = users_df['user_count'].sum()

    return dynamic_values







 
def fetch_dynamic_values_for_date_range(start_date, end_date=None):
    """Fetches dynamic values from the database for a given date range."""
    
    # Create a list to store individual DataFrames for each dynamic value
    dataframes = []

    # Get number of pipelines with source 'push'
    pipelines_df = get_num_pipeline_on_push(start_date, end_date)
    if not pipelines_df.empty:
        pipelines_df = pipelines_df.rename(columns={'pipeline_count': 'num_pipeline_on_push'})
        dataframes.append(pipelines_df)

    # Get number of commits
    commits_df = get_num_commits(start_date, end_date)
    if not commits_df.empty:
        commits_df = commits_df.rename(columns={'commit_count': 'num_commits'})
        dataframes.append(commits_df)

    # Get number of projects created
    projects_df = get_num_projects(start_date, end_date)
    if not projects_df.empty:
        projects_df = projects_df.rename(columns={'project_count': 'num_projects'})
        dataframes.append(projects_df)

    # Get number of users added
    users_df = get_num_users(start_date, end_date)
    if not users_df.empty:
        users_df = users_df.rename(columns={'user_count': 'num_users'})
        dataframes.append(users_df)

    # Merge all DataFrames on 'month_year'
    if dataframes:
        dynamic_values_df = dataframes[0]
        for df in dataframes[1:]:
            dynamic_values_df = dynamic_values_df.merge(df, on='month_year', how='outer')
        dynamic_values_df = dynamic_values_df.fillna(0)
        return dynamic_values_df
    else:
        return pd.DataFrame()



def calculate_monthly_savings(process_data, dynamic_values_df):
    """
    Calculate monthly savings based on process data and dynamic values.
    
    Args:
    - process_data (list): List of dictionaries containing process details.
    - dynamic_values_df (pd.DataFrame): DataFrame containing dynamic values for each month.
    
    Returns:
    - dict: Monthly detailed breakdown of savings.
    """

    # Initialize an empty dictionary to hold the results
    monthly_savings = {}

    # Check if all dynamic values are present in dynamic_values_df
    for process in process_data:
        for dynamic_value in process['dynamic_values']:
            if dynamic_value not in dynamic_values_df.columns:
                raise ValueError(f"Error: The dynamic value '{dynamic_value}' does not exist in the dataframe and needs to be added to the dynamic_values file.")
    
    
    # Iterate over each month in the dynamic_values_df
    for month, month_data in dynamic_values_df.iterrows():
        # print("Month (Index):", month)
        # print("Data for the Month:", month_data)
        monthly_detail = []

        # Calculate the savings for each process
        for process in process_data:
            before_time = process['before_process']['time_hrs']
            after_time = process['after_process']['time_hrs']
            dynamic_value = list(process['dynamic_values'].keys())[0]

            hours_saved = (before_time - after_time) * month_data[dynamic_value]
            cost_saved = hours_saved * process['hourly_rate']

            monthly_detail.append({
                "process_name": process['process_name'],
                "hours_saved": hours_saved,
                "cost_saved": cost_saved
            })

        # Convert the month from 'YYYY-MM' format to 'Month YYYY' format
        formatted_month = datetime.strptime(month_data["month_year"], '%Y-%m').strftime('%B %Y')

        monthly_savings[formatted_month] = monthly_detail

    return monthly_savings
 



def get_value_over_time(start_date, end_date=None):

    with open('src/value/savings_input.json', 'r') as file:
        process_data = json.load(file)

    # Fetch dynamic values for the given date range.
    dynamic_values_df = fetch_dynamic_values_for_date_range(start_date, end_date)

    # Calculate monthly savings.
    savings = calculate_monthly_savings(process_data, dynamic_values_df)

    # Print the results json formatting
    return savings

def get_value_over_time_for_ui(start_date, end_date=None):
    """
    Reformats the savings data to a structure suitable for CoreUI data tables.

    Args:
    - savings_data (dict): Output from get_value_over_time function.

    Returns:
    - dict: Reformatted data.
    """
    reformatted_data = {}
    savings_data = get_value_over_time(start_date, end_date)
    for month, processes in savings_data.items():
        for process in processes:
            process_name = process["process_name"]
            if process_name not in reformatted_data:
                reformatted_data[process_name] = {}
            
            reformatted_data[process_name][month] = {
                "hours_saved": process["hours_saved"],
                "cost_saved": process["cost_saved"]
            }

    return reformatted_data



if __name__ == "__main__":

    start_date = '2023-01-01'
    end_date = '2023-12-31'
    print(get_value_over_time_for_ui(start_date, end_date))