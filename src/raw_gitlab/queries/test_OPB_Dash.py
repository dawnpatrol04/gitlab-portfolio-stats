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
),

docker_analysis AS (
    SELECT
        project_id,
        COUNT(CASE WHEN LOWER(file_name) NOT LIKE 'dockerfile' THEN 1 END) AS count_not_dockerfile,
        COUNT(file_name) AS total_files,
        COUNT(CASE WHEN image_name NOT LIKE '%jaov%' THEN 1 END) AS count_image_not_jaov,
        CASE 
            WHEN COUNT(file_name)  = 0 THEN ''
            WHEN COUNT(CASE WHEN image_name NOT LIKE '%jaov%' THEN 1 END) != 0 THEN '4'
            WHEN COUNT(CASE WHEN LOWER(file_name) NOT LIKE 'dockerfile' THEN 1 END) > 1 THEN '4'
            WHEN COUNT(file_name) = 1 AND COUNT(CASE WHEN LOWER(file_name) NOT LIKE 'dockerfile' THEN 1 END) = 0 THEN '4'
            ELSE ''
        END AS container_badge
    FROM docker_search
    GROUP BY project_id
),

cicd_analysis AS (
    SELECT
        project_id,
        CASE 
            WHEN SUM(CASE WHEN lower(file_name)  = 'jenkinsfile' THEN 1 ELSE 0 END) > 0 THEN '4'
            WHEN SUM(CASE WHEN file_name = '.gitlab-ci.yml' THEN 1 ELSE 0 END) > 0 THEN '1'
            ELSE ''
        END AS cicd_badge
    FROM (
        SELECT project_id, file_name FROM jenkins_search
        UNION ALL
        SELECT project_id, file_name FROM gitlabci_search
    ) combined
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
    END AS activity_badge,
    COALESCE(ba.branch_count, 0) AS branch_count,
    COALESCE(ba.has_main_or_master, 0) AS has_main_or_master,
    COALESCE(ba.has_dev, 0) AS has_dev,
    1 + -- 1 point because they're in GitLab
    COALESCE(ba.has_main_or_master, 0) +
    COALESCE(ba.has_dev, 0) +
    CASE WHEN COALESCE(ba.branch_count, 0) < 5 THEN 1 ELSE 0 END AS src_ctl_badge,
    COALESCE(rp.pipeline_count_last_6_months, 0) AS pipeline_count_last_6_months,
    COALESCE(gcs.runner_name, '') AS runner_name,
        CASE
        WHEN COALESCE(rp.pipeline_count_last_6_months, 0) > 0 AND COALESCE(gcs.runner_name, '') = '' THEN '4'
        WHEN COALESCE(gcs.runner_name, '') != '' THEN '1'
        ELSE ''
    END AS compute_badge,
    COALESCE(es.contains_cyberark, 0) AS cyberark,
    COALESCE(da.count_not_dockerfile, 0) AS count_not_dockerfile,
    COALESCE(da.total_files, 0) AS total_files,
    COALESCE(da.count_image_not_jaov, 0) AS count_image_not_jaov,
 COALESCE(da.container_badge, '') AS container_badge,
    COALESCE(ca.cicd_badge, '') AS cicd_badge -- This is the new column added to the main query
FROM projects_v2 p
JOIN users u ON p.creator_id = u.id
LEFT JOIN branch_aggregation ba ON p.id = ba.project_id
LEFT JOIN recent_pipelines rp ON p.id = rp.project_id
LEFT JOIN gitlabci_search gcs ON p.id = gcs.project_id
LEFT JOIN env_search es ON p.id = es.project_id
LEFT JOIN docker_analysis da ON p.id = da.project_id
LEFT JOIN cicd_analysis ca ON p.id = ca.project_id; -- Join with cicd_analysis on project_id


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
