import json
import os

import gitlab
import pandas as pd
import requests
from dotenv import find_dotenv, load_dotenv

from src.utils.database import connect_to_db
from src.utils.gitlab_connect import connect_to_gitlab
from src.utils.logger import setup_logger

load_dotenv(find_dotenv())
GITLAB_URL = os.getenv('GITLAB_URL')
GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
logger = setup_logger("gitlab_logger", "gitlab_log.txt")

# Helper functions
def file_exists(project, file_name):
    default_branch = project.default_branch
    try:
        project.files.get(file_path=file_name, ref=default_branch)
        return True
    except gitlab.exceptions.GitlabGetError:
        return False



def get_file_link(gl, project, file_name):
    return f"{gl.url}/{project.namespace['full_path']}/{project.path}/-/blob/master/{file_name}"

def extract_docker_image(docker_content):
    if not docker_content:
        return None  # or return an empty string: return ""
    
    for line in docker_content.split('\n'):
        if line.strip().startswith('FROM'):
            return line.split()[1]  # Return the image name after "FROM"
    
    return None



def fetch_file_content(project, file_name):
    content = None
    default_branch = project.default_branch
    try:
        file_obj = project.files.get(file_path=file_name, ref=default_branch)
        base64_content = file_obj.decode()  # Decoding base64
        content = base64_content.decode('utf-8')  # Converting bytes to string
    except gitlab.exceptions.GitlabGetError:
        pass
    return content



def fetch_ci_data(gl, project):
    ci_data = {}
    ci_data['ci_file_exists'] = file_exists(project, '.gitlab-ci.yml')
    ci_data['ci_file_link'] = get_file_link(gl, project, '.gitlab-ci.yml') if ci_data['ci_file_exists'] else None
    ci_content = fetch_file_content(project, '.gitlab-ci.yml') if ci_data['ci_file_exists'] else None
    ci_data['ci_first_line'] = ci_content.split('\n')[0] if ci_content else None
    return ci_data

def fetch_docker_data(gl, project):
    docker_data = {}
    docker_data['docker_file_exists'] = file_exists(project, 'Dockerfile')
    docker_data['docker_file_link'] = get_file_link(gl, project, 'Dockerfile') if docker_data['docker_file_exists'] else None
    docker_content = fetch_file_content(project, 'Dockerfile') if docker_data['docker_file_exists'] else None
    docker_data['docker_image'] = extract_docker_image(docker_content)
    return docker_data

def fetch_env_data(gl, project, key="CYBERARK"):
    """Fetches the value of a specified key from the .env file."""
    env_data = {}
    env_data['env_file_exists'] = file_exists(project, 'example.env')
    env_data['env_file_link'] = get_file_link(gl, project, 'example.env') if env_data['env_file_exists'] else None
    env_content = fetch_file_content(project, 'example.env') if env_data['env_file_exists'] else None
    env_data[key] = extract_env_value(env_content, key)
    return env_data

def extract_env_value(env_content, key):
    """Extracts the value of a specified key from the .env content."""
    if env_content:
        for line in env_content.split('\n'):
            if line.startswith(key + '='):
                return line.split('=')[1]
    return None


def get_project_attributes(project):
    """Get all attributes of a project object that can be serialized."""
    serializable_types = (int, float, str, bool, type(None))  # Add other types as necessary
    return {attr: getattr(project, attr) for attr in dir(project)
            if not callable(getattr(project, attr))
            and not attr.startswith("_")
            and isinstance(getattr(project, attr), serializable_types)}


def fetch_repository_size(project_id):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}"
    headers = {"Authorization": f"Bearer {GITLAB_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    return data.get('statistics', {}).get('repository_size', None)







def fetch_gitlab_data(group_name):
    gl = connect_to_gitlab()
    group = gl.groups.get(group_name)
    gitlab_projects = group.projects.list(all=True, include_subgroups=True)
    projects_list = []

    for project in gitlab_projects:
        full_project = gl.projects.get(project.id)

        # Fetching the project's statistics using the defined function
        repository_size = fetch_repository_size(full_project.id)

        project_data = {
            'name': full_project.name,
            'repository_size': repository_size,  # Storing the repository_size in the data
            'ui': True,  # Placeholder column
            'batch': True,  # Placeholder column
            'branch_count': 3  # Placeholder column
        }
        project_data.update(get_project_attributes(full_project))
        project_data.update(fetch_ci_data(gl, full_project))
        project_data.update(fetch_docker_data(gl, full_project))
        project_data.update(fetch_env_data(gl, full_project))

        projects_list.append(project_data)

    return pd.DataFrame(projects_list)





def process_dataframe(df):
    for column in df.columns:
        if df[column].apply(type).eq(list).any():
            # Convert lists to JSON string
            df[column] = df[column].apply(json.dumps)
        elif df[column].apply(type).eq(dict).any():
            # Convert dictionaries to JSON string
            df[column] = df[column].apply(json.dumps)
    return df

def save_data_to_db(df):
    df = process_dataframe(df)  # Process the dataframe before saving
    with connect_to_db() as conn:
        df.to_sql("projects_v2", conn, if_exists="replace", index=False)


def refresh_gitlab_data(group_name):
    df = fetch_gitlab_data(group_name)
    save_data_to_db(df)
    return {"status": "success", "message": f"Data for group {group_name} refreshed successfully!"}

if __name__ == "__main__":

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    group_name = "test-group"
    # df = fetch_gitlab_data(group_name)
    # save_data_to_db(df)
    # print(df)
    refresh_gitlab_data(group_name)
    all_df = pd.read_sql("select * from projects_v2", connect_to_db())
    # save data to csv
    # all_df.to_csv('projects_v2.csv', index=False)
    print(all_df)

