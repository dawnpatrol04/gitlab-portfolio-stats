import pandas as pd
from src.utils.database import connect_to_db
import re
import yaml
def extract_docker_image(content):
    """Extract the image name from Dockerfile content."""
    match = re.search(r'^FROM\s+([^\s]+)', content, re.MULTILINE)
    return match.group(1) if match else None

 
def extract_version_from_yaml(content):
    """Extract the version from .gitlab-ci.yml content."""
    data = yaml.safe_load(content)
    return data.get('_version', None)

def extract_gitlab_runner(content):
    """Extract the default runner tag from .gitlab-ci.yml content."""
    try:
        data = yaml.safe_load(content)
        tags = data.get('default', {}).get('tags', [])
        if tags:
            return tags[0]
        else:
            return None
    except Exception as e:
        print(f"Error parsing YAML: {e}")
        return None


def search_cyberark_in_env(content):
    """Check for cyberark in .env content."""
    return 'cyberark' in content.lower()

def enrich_project_file_data():
    # Connect to the database
    with connect_to_db() as conn:
        # Process Dockerfiles
        docker_df = pd.read_sql("SELECT * FROM docker_search", conn)
        docker_df['image_name'] = docker_df['file_content'].apply(extract_docker_image)
        docker_df.to_sql('docker_search', conn, index=False, if_exists='replace')

         # Process .gitlab-ci.yml files
        gitlabci_df = pd.read_sql("SELECT * FROM gitlabci_search", conn)
        gitlabci_df['runner_name'] = gitlabci_df['file_content'].apply(extract_gitlab_runner)
        gitlabci_df['file_version'] = gitlabci_df['file_content'].apply(extract_version_from_yaml)  # Add this line to extract the version
        gitlabci_df.to_sql('gitlabci_search', conn, index=False, if_exists='replace')

        # Process .env files
        env_df = pd.read_sql("SELECT * FROM env_search", conn)
        env_df['contains_cyberark'] = env_df['file_content'].apply(search_cyberark_in_env)
        env_df.to_sql('env_search', conn, index=False, if_exists='replace')

if __name__ == "__main__":
    enrich_project_file_data()
