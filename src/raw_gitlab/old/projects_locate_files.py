import gitlab
from src.utils.database import connect_to_db
from src.utils.gitlab_connect import connect_to_gitlab
from src.utils.logger import setup_logger
import os
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())


FILES = ['Dockerfile', 'Jenkinsfile', '.gitlab-ci.yml', 'example.env']

# Connect to GitLab
gl = connect_to_gitlab()

# Fetch all the projects within a group
def get_all_projects_in_group(group_name):
    group = gl.groups.get(group_name)
    return group.projects.list(all=True, include_subgroups=True)


# Recursively search the tree for specific files
def search_project_tree_for_files(project, files_to_search, path=''):
    tree = project.repository_tree(path=path, all=True)
    found_files = {file.lower(): None for file in files_to_search}

    for item in tree:
        lower_name = item['name'].lower()
        if lower_name in found_files:
            found_files[lower_name] = item['path']
        # If the item is a directory, search recursively
        elif item['type'] == 'tree':
            found_files_in_subdir = search_project_tree_for_files(project, files_to_search, path=item['path'])
            # Update found_files with any found paths from the subdir
            found_files.update({k: v for k, v in found_files_in_subdir.items() if v})

    return {k: (found_files[k.lower()] if k.lower() in found_files else None) for k in files_to_search}

######  Working with files found in project tree  ######

# Given the location of a Dockerfile, extract the image name
def get_image_name_from_dockerfile(project, dockerfile_path):
    try:
        dockerfile_content = project.files.get(file_path=dockerfile_path, ref=project.default_branch).decode().decode('utf-8')
        for line in dockerfile_content.splitlines():
            if line.strip().startswith('FROM '):
                return line.split()[1]
    except gitlab.exceptions.GitlabGetError:
        print(f"Error fetching Dockerfile from path {dockerfile_path} in project {project.name}")
    return None


def main():
    group_name = os.getenv("GITLAB_GROUP") # Replace with the name of your group
    all_projects = get_all_projects_in_group(group_name)

    for project in all_projects:
        full_project = gl.projects.get(project.id)
        file_locations = search_project_tree_for_files(full_project, FILES)

        dockerfile_location = file_locations.get('Dockerfile')
        if dockerfile_location:  # Only get the image name if Dockerfile exists
            image_name = get_image_name_from_dockerfile(full_project, dockerfile_location)
        else:
            image_name = None

        # Print the results
        print(f"Project: {full_project.name}")
        for file_name, location in file_locations.items():
            print(f"{file_name}: {location is not None}")
        if image_name:
            print(f"Dockerfile Image: {image_name}")
        print("-" * 40)

if __name__ == "__main__":
    main()
