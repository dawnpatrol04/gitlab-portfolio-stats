import pandas as pd
from src.utils.database import connect_to_db

def get_file_counts_by_project():
    # Get the database connection from connect_to_db
    connection = connect_to_db()
    
    # Define the SQL query
    query = """

 
WITH 
branch_aggregation AS (
    SELECT 
        project_id,
        COUNT(DISTINCT name) AS branch_count,
        MAX(CASE WHEN name IN ('main', 'master') THEN 1 ELSE 0 END) AS has_main_or_master,
        MAX(CASE WHEN name = 'dev' THEN 1 ELSE 0 END) AS has_dev
    FROM branches
    GROUP BY project_id
),

recent_pipelines AS (
    SELECT 
        project_id,
        COUNT(pipeline_id) AS pipeline_count_last_6_months
    FROM pipelines
    WHERE 
        created_at >= date('now', '-6 months')
    GROUP BY project_id
)

SELECT 
    p.id AS project_id, 
    p.name AS project_name,
    u.avatar_url AS user_icon,
    u.id AS user_id,
    (CAST(strftime('%Y', 'now') AS INTEGER) - CAST(SUBSTR(p.last_activity_at, 1, 4) AS INTEGER)) * 12 +
    (CAST(strftime('%m', 'now') AS INTEGER) - CAST(SUBSTR(p.last_activity_at, 6, 2) AS INTEGER)) AS months_since_last_activity,
    CASE
        WHEN (CAST(strftime('%Y', 'now') AS INTEGER) - CAST(SUBSTR(p.last_activity_at, 1, 4) AS INTEGER)) * 12 +
             (CAST(strftime('%m', 'now') AS INTEGER) - CAST(SUBSTR(p.last_activity_at, 6, 2) AS INTEGER)) <= 1 THEN 1
        WHEN (CAST(strftime('%Y', 'now') AS INTEGER) - CAST(SUBSTR(p.last_activity_at, 1, 4) AS INTEGER)) * 12 +
             (CAST(strftime('%m', 'now') AS INTEGER) - CAST(SUBSTR(p.last_activity_at, 6, 2) AS INTEGER)) <= 3 THEN 2
        WHEN (CAST(strftime('%Y', 'now') AS INTEGER) - CAST(SUBSTR(p.last_activity_at, 1, 4) AS INTEGER)) * 12 +
             (CAST(strftime('%m', 'now') AS INTEGER) - CAST(SUBSTR(p.last_activity_at, 6, 2) AS INTEGER)) <= 6 THEN 3
        ELSE 4 
    END AS activity_icon,
    COALESCE(ba.branch_count, 0) AS branch_count,
    COALESCE(ba.has_main_or_master, 0) AS has_main_or_master,
    COALESCE(ba.has_dev, 0) AS has_dev,
    1 + -- 1 point because they're in GitLab
    COALESCE(ba.has_main_or_master, 0) +
    COALESCE(ba.has_dev, 0) +
    CASE WHEN COALESCE(ba.branch_count, 0) < 5 THEN 1 ELSE 0 END AS src_ctl_badge,
    COALESCE(rp.pipeline_count_last_6_months, 0) AS pipeline_count_last_6_months,
     COALESCE(gcs.runner_name,'' ) AS runner_name
FROM projects_v2 p
JOIN users u ON p.creator_id = u.id
LEFT JOIN branch_aggregation ba ON p.id = ba.project_id
LEFT JOIN recent_pipelines rp ON p.id = rp.project_id
LEFT JOIN gitlabci_search gcs ON p.id = gcs.project_id;  -- Joining with gitlabci_search on project_id






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
