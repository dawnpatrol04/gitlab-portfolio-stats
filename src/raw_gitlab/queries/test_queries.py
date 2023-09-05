import pandas as pd
from src.utils.database import connect_to_db

def get_file_counts_by_project():
    # Get the database connection from connect_to_db
    connection = connect_to_db()
    
    # Define the SQL query
    query = """
    WITH aggregated AS (
        SELECT
            project_id,
            project_name,
            COUNT(CASE WHEN file_type = 'Dockerfile' THEN 1 END) AS Dockerfiles,
            COUNT(CASE WHEN file_type = 'Jenkinsfile' THEN 1 END) AS Jenkinsfiles,
            COUNT(CASE WHEN file_type = '.gitlab-ci' THEN 1 END) AS gitlab_cis,
            COUNT(CASE WHEN file_type = '.env' THEN 1 END) AS envs,
            MAX(CASE WHEN file_type = 'Dockerfile' THEN file_url ELSE NULL END) AS Dockerfile_file_url,
            MAX(CASE WHEN file_type = 'Jenkinsfile' THEN file_url ELSE NULL END) AS Jenkinsfile_file_url,
            MAX(CASE WHEN file_type = '.gitlab-ci' THEN file_url ELSE NULL END) AS gitlab_ci_file_url,
            MAX(CASE WHEN file_type = '.env' THEN file_url ELSE NULL END) AS env_file_url
        FROM (
            SELECT project_id, project_name, 'Dockerfile' AS file_type, file_url FROM docker_search
            UNION ALL
            SELECT project_id, project_name, 'Jenkinsfile' AS file_type, file_url FROM jenkins_search
            UNION ALL
            SELECT project_id, project_name, '.gitlab-ci' AS file_type, file_url FROM gitlabci_search
            UNION ALL
            SELECT project_id, project_name, '.env' AS file_type, file_url FROM env_search
        ) sub
        GROUP BY project_id, project_name
    )
    SELECT
        a.*,
        d.image_name,
        g.runner_name,
        e.contains_cyberark
    FROM aggregated a
    LEFT JOIN docker_search d ON a.project_id = d.project_id
    LEFT JOIN gitlabci_search g ON a.project_id = g.project_id
    LEFT JOIN env_search e ON a.project_id = e.project_id;
    """

    # Fetch data into a DataFrame
    df = pd.read_sql(query, connection)
    connection.close()
    
    return df

# Example usage:
df = get_file_counts_by_project()
# show all columns
pd.set_option('display.max_columns', None)
print(df)
# save to CSV
df.to_csv('project_file_data.csv', index=False)
