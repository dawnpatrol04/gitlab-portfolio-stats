
import gitlab
import pandas as pd
from dotenv import find_dotenv, load_dotenv
import os
from src.utils.database import connect_to_db
from src.utils.gitlab_connect import connect_to_gitlab
from src.utils.logger import setup_logger

load_dotenv(find_dotenv())

logger = setup_logger("gitlab_logger", "gitlab_log.txt")

def get_pipeline_attributes(pipeline):
    """Get all attributes of a pipeline object that can be serialized."""
    serializable_types = (int, float, str, bool, type(None))
    return {attr: getattr(pipeline, attr) for attr in dir(pipeline)
            if not callable(getattr(pipeline, attr))
            and not attr.startswith("_")
            and isinstance(getattr(pipeline, attr), serializable_types)}

def fetch_gitlab_pipeline_data(group_name):
    logger.info("Fetching pipelines for GitLab group: %s", group_name)
    
    gl = connect_to_gitlab()
    group = gl.groups.get(group_name)
    gitlab_projects = group.projects.list(all=True, include_subgroups=True)

    pipelines_list = []

    for project in gitlab_projects:
        full_project = gl.projects.get(project.id)
        try:
            gitlab_pipelines = full_project.pipelines.list(all=True)
        except gitlab.exceptions.GitlabListError as e:
            logger.warning(f"Failed to retrieve pipelines for project {project.id}: {e}")
            continue

        for pipeline in gitlab_pipelines:
            pipeline_data = {
                'pipeline_id': pipeline.id,
                'project_id': project.id
            }
            pipeline_data.update(get_pipeline_attributes(pipeline))
            pipelines_list.append(pipeline_data)

    logger.info("Finished fetching data for %d pipelines", len(pipelines_list))
    return pd.DataFrame(pipelines_list)

def save_pipeline_data_to_db(df):
    with connect_to_db() as conn:
        df.to_sql("pipelines", conn, if_exists="replace", index=False)

def refresh_pipeline_data(group_name):
    df = fetch_gitlab_pipeline_data(group_name)
    save_pipeline_data_to_db(df)
    return {"status": "success", "message": f"Pipeline data for group {group_name} refreshed successfully!"}

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    group_name = os.getenv("GITLAB_GROUP")
    refresh_pipeline_data(group_name)
    all_df = pd.read_sql("select * from pipelines", connect_to_db())
    print(all_df)
