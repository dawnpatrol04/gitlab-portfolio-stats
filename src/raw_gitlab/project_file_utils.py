import os

import pandas as pd
from dotenv import find_dotenv, load_dotenv

from src.utils.database import connect_to_db
from src.utils.gitlab_connect import connect_to_gitlab
from src.utils.logger import setup_logger

load_dotenv(find_dotenv())
logger = setup_logger("gitlab_logger", "gitlab_log.txt")

# Connect to GitLab
gl = connect_to_gitlab()

project_trees = {}

def get_all_projects_in_group(group_name):
    logger.info(f"Fetching all projects in group: {group_name}")
    group = gl.groups.get(group_name)
    return group.projects.list(all=True, include_subgroups=True)

def search_project_tree_for_files(project, file_to_search, wildcard=False, path=''):
    if not path:
        tree = project_trees.get(project.id)
    else:
        tree = project.repository_tree(path=path, all=True)

    found_files = []

    for item in tree:
        lower_name = item['name'].lower()
        if wildcard and file_to_search.lower() in lower_name:
            found_files.append({
                'name': item['name'],
                'path': item['path']
            })
        elif lower_name == file_to_search.lower():
            found_files.append({
                'name': item['name'],
                'path': item['path']
            })

        # If the item is a directory, search recursively
        if item['type'] == 'tree':
            found_files.extend(search_project_tree_for_files(project, file_to_search, wildcard, path=item['path']))

    return found_files

def search_and_save_gitlab_files(table_name, file_to_search, wildcard=False):
    group_name = os.getenv('GITLAB_GROUP')
    logger.info("Initiating search...")
    all_projects = get_all_projects_in_group(group_name)

    # Fetch and store tree for each project upfront
    for project in all_projects:
        full_project = gl.projects.get(project.id)
        project_trees[full_project.id] = full_project.repository_tree(all=True)

    all_data = []

    for project in all_projects:
        logger.info(f"Searching in project: {project.name}")
        full_project = gl.projects.get(project.id)
        found_files = search_project_tree_for_files(full_project, file_to_search, wildcard)

        for file in found_files:
            file_content = full_project.files.get(file_path=file['path'], ref=full_project.default_branch).decode().decode('utf-8')
            file_url = f"{full_project.web_url}/blob/{full_project.default_branch}/{file['path']}"
            all_data.append({
                'project_id': full_project.id,
                'project_name': full_project.name,
                'file_name': file['name'],
                'file_url': file_url,
                'file_content': file_content
            })

    # Save the data using pandas
    logger.info(f"Saving data to table {table_name}")
    df = pd.DataFrame(all_data)
    with connect_to_db() as conn:
        df.to_sql(table_name, conn, index=False, if_exists='replace')

    logger.info(f"Data saved to {table_name} for file search '{file_to_search}'")

if __name__ == "__main__":
    table_name = "docker_search"  # Replace with your table name
    file_to_search = 'Dockerfile'
    search_and_save_gitlab_files(table_name, file_to_search, wildcard=True)
    
    pd.set_option('display.max_colwidth', None) 
    with connect_to_db() as conn:
        df = pd.read_sql(f"SELECT file_url FROM {table_name}", conn)
    print(df)
