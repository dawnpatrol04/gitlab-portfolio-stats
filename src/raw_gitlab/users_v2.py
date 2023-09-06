import pandas as pd
from dotenv import find_dotenv, load_dotenv

from src.utils.database import connect_to_db
from src.utils.gitlab_connect import connect_to_gitlab
from src.utils.logger import setup_logger

load_dotenv(find_dotenv())
 
logger = setup_logger("gitlab_logger", "gitlab_log.txt")
 
def get_project_attributes(project):
    """Get all attributes of a project object that can be serialized."""
    serializable_types = (int, float, str, bool, type(None))  # Add other types as necessary
    return {attr: getattr(project, attr) for attr in dir(project)
            if not callable(getattr(project, attr))
            and not attr.startswith("_")
            and isinstance(getattr(project, attr), serializable_types)}

def fetch_gitlab_data(group_name):
    logger.info("Fetching data for GitLab group: %s", group_name)
    
    gl = connect_to_gitlab()
    group = gl.groups.get(group_name)
    gitlab_projects = group.projects.list(all=True, include_subgroups=True)

    projects_list = []

    for project in gitlab_projects:
        logger.info("Fetching data for project %s", project.id)
        full_project = gl.projects.get(project.id)
        project_data = {
            'name': full_project.name,
        }
        project_data.update(get_project_attributes(full_project))
        projects_list.append(project_data)

    logger.info("Finished fetching data for %d projects", len(projects_list))
    return pd.DataFrame(projects_list)

def save_data_to_db(df):
    with connect_to_db() as conn:
        df.to_sql("projects_v2", conn, if_exists="replace", index=False)

def refresh_project_data(group_name):
    df = fetch_gitlab_data(group_name)
    save_data_to_db(df)
    return {"status": "success", "message": f"Data for group {group_name} refreshed successfully!"}

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    group_name = "test-group"
    refresh_project_data(group_name)
    all_df = pd.read_sql("select * from projects", connect_to_db())
    print(all_df)
