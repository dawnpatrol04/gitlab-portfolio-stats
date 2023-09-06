
import gitlab
import pandas as pd
from dotenv import find_dotenv, load_dotenv

from src.utils.database import connect_to_db
from src.utils.gitlab_connect import connect_to_gitlab
from src.utils.logger import setup_logger

load_dotenv(find_dotenv())

logger = setup_logger("gitlab_logger", "gitlab_log.txt")

def get_branch_attributes(branch):
    """Get all attributes of a branch object that can be serialized."""
    serializable_types = (int, float, str, bool, type(None))
    return {attr: getattr(branch, attr) for attr in dir(branch)
            if not callable(getattr(branch, attr))
            and not attr.startswith("_")
            and isinstance(getattr(branch, attr), serializable_types)}

def fetch_gitlab_branch_data(group_name):
    logger.info("Fetching branches for GitLab group: %s", group_name)
    
    gl = connect_to_gitlab()
    group = gl.groups.get(group_name)
    gitlab_projects = group.projects.list(all=True, include_subgroups=True)

    branches_list = []

    for project in gitlab_projects:
        full_project = gl.projects.get(project.id)  # Get the full project details
        gitlab_branches = full_project.branches.list(all=True)  # Fetch branches for the full project
        for branch in gitlab_branches:
            logger.info("Fetching data for branch %s of project %s", branch.name, project.id)
            branch_data = {
                'branch_name': branch.name,
                'project_id': project.id
            }
            branch_data.update(get_branch_attributes(branch))
            branches_list.append(branch_data)

    logger.info("Finished fetching data for %d branches", len(branches_list))
    return pd.DataFrame(branches_list)


def save_branch_data_to_db(df):
    with connect_to_db() as conn:
        df.to_sql("branches", conn, if_exists="replace", index=False)

def refresh_branch_data(group_name):
    df = fetch_gitlab_branch_data(group_name)
    save_branch_data_to_db(df)
    return {"status": "success", "message": f"Branch data for group {group_name} refreshed successfully!"}

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    group_name = "test-group"
    refresh_branch_data(group_name)
    all_df = pd.read_sql("select * from branches", connect_to_db())
    print(all_df)
