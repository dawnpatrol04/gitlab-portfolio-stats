import pandas as pd

from src.raw_gitlab.project_file_data_enrich import enrich_project_file_data
from src.utils.database import connect_to_db
from src.utils.gitlab_connect import connect_to_gitlab
from src.utils.logger import setup_logger

logger = setup_logger("gitlab_logger", "gitlab_log.txt")
import os
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())
# Connect to GitLab
gl = connect_to_gitlab()

def get_all_projects_in_group(group_name):
    logger.info(f"Fetching all projects in group: {group_name}")
    group = gl.groups.get(group_name)
    return group.projects.list(all=True, include_subgroups=True)

def fetch_all_project_trees(group_name):
    all_projects = get_all_projects_in_group(group_name)
    project_trees = {}
    for project in all_projects:
        full_project = gl.projects.get(project.id)
        logger.info(f"Pull Tree - {project.id}")
        try:
            project_trees[full_project.id] = full_project.repository_tree(all=True)
        except Exception as e:
            logger.error(f"pull tree error {project.id} - {e}")
    return project_trees

def search_project_tree_for_files(project, file_to_search, project_trees, wildcard=False, path=''):
    tree = project_trees.get(project.id, []) if not path else project.repository_tree(path=path, all=True)
    found_files = []

    for index, item in enumerate(tree, start=1):
        lower_name = item['name'].lower()
        
        # Logging the current item being processed
        logger.info(f"Processing {index}/{len(tree)}: {item['name']} in project {project.name}")

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
            logger.info(f"Entering directory {item['name']} in project {project.name}")
            found_files.extend(search_project_tree_for_files(project, file_to_search, project_trees, wildcard, path=item['path']))

    return found_files


    return found_files

def search_and_save_gitlab_files(table_name, file_to_search, project_trees, wildcard=False):
    group_name = os.getenv('GITLAB_GROUP')
    logger.info("Initiating search...")
    all_projects = get_all_projects_in_group(group_name)

    all_data = []
    for project in all_projects:
        logger.info(f"Searching in project: {project.name}")
        full_project = gl.projects.get(project.id)
        found_files = search_project_tree_for_files(full_project, file_to_search, project_trees, wildcard)

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
def process_and_enrich_gitlab_data():
    # Fetch the project trees
    project_trees = fetch_all_project_trees(os.getenv('GITLAB_GROUP'))
    
    # Search and save files for each type
    search_and_save_gitlab_files('docker_search', 'Dockerfile', project_trees, wildcard=True)
    search_and_save_gitlab_files('jenkins_search', 'Jenkinsfile', project_trees, wildcard=True)
    search_and_save_gitlab_files('gitlabci_search', '.gitlab-ci', project_trees, wildcard=True)
    search_and_save_gitlab_files('env_search', '.env', project_trees, wildcard=True)
    
    # Enrich the data with additional details
    enrich_project_file_data()
    
    # Display the result URLs
    pd.set_option('display.max_colwidth', None) 
    for table in ['docker_search', 'jenkins_search', 'gitlabci_search', 'env_search']:
        with connect_to_db() as conn:
            df = pd.read_sql(f"SELECT file_url FROM {table}", conn)
        print(df)

if __name__ == "__main__":
    process_and_enrich_gitlab_data()