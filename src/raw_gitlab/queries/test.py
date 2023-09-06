import pandas as pd
from src.utils.database import connect_to_db

def get_file_counts_by_project():
    # Get the database connection from connect_to_db
    connection = connect_to_db()
    
    # Define the SQL query
    query = """
    select * from gitlabci_search;
    """

    # Fetch data into a DataFrame
    df = pd.read_sql(query, connection)
    connection.close()
    
    return df

# Example usage:
df = get_file_counts_by_project()
# show all columns
pd.set_option('display.max_columns', None)
# max with for coluns
pd.set_option('display.max_colwidth', None)
print(df)
# save to CSV
df.to_csv('project_file_data.csv', index=False)
