from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from src.utils.database import connect_to_db
from src.utils.gitlab_connect import connect_to_gitlab
from src.utils.logger import setup_logger

logger = setup_logger("gitlab_logger", "gitlab_log.txt")

@dataclass
class Project:
    id: int
    description: str
    default_branch: str
    visibility: str
    ssh_url_to_repo: str
    http_url_to_repo: str
    http_url_to_repo: str
    web_url: str
    name: str
    name_with_namespace: str
    path: str
    path_with_namespace: str
    issues_enabled: bool
    open_issues_count: int
    jobs_enabled: bool
    wiki_enabled: bool
    snippets_enabled: bool
    resolve_outdated_diff_discussions: bool
    container_registry_enabled: bool
    created_at: datetime
    last_activity_at: datetime
    creator_id: int
    namespace: dict
    import_status: str
    archived: bool
    avatar_url: str
    shared_runners_enabled: bool
    # marked_for_deletion_at: str
    is_example_project: bool



class ProjectsDataRetriever:
    stored_projects = []  # This will store the projects data

    def __init__(self):
        self.gl = connect_to_gitlab()

    def get_all_projects(self, group_name):
        group = self.gl.groups.get(group_name)
        gitlab_projects = group.projects.list(all=True, include_subgroups=True)

        example_projects = [
            # ... [list of projects as you've provided]
        ]

        for project in gitlab_projects:
            proj = Project(
                id=project.id,
                description=project.description,
                default_branch=project.default_branch,
                visibility=project.visibility,
                ssh_url_to_repo=project.ssh_url_to_repo,
                http_url_to_repo=project.http_url_to_repo,
                web_url=project.web_url,
                name=project.name,
                name_with_namespace=project.name_with_namespace,
                path=project.path,
                path_with_namespace=project.path_with_namespace,
                issues_enabled=project.issues_enabled,
                open_issues_count=project.open_issues_count,
                jobs_enabled=project.jobs_enabled,
                wiki_enabled=project.wiki_enabled,
                snippets_enabled=project.snippets_enabled,
                resolve_outdated_diff_discussions=project.resolve_outdated_diff_discussions,
                container_registry_enabled=project.container_registry_enabled,
                created_at=datetime.strptime(project.created_at, '%Y-%m-%dT%H:%M:%S.%fZ'),
                last_activity_at=datetime.strptime(project.last_activity_at, '%Y-%m-%dT%H:%M:%S.%fZ'),
                creator_id=project.creator_id,
                namespace=project.namespace,
                import_status=project.import_status,
                archived=project.archived,
                avatar_url=project.avatar_url,
                shared_runners_enabled=project.shared_runners_enabled,
                is_example_project=project.path_with_namespace in example_projects
            )
            self.stored_projects.append(proj)  # Store the data in the class variable


    def retrieve_data(self, group_name):
        logger.info("Starting data retrieval...")
        self.get_all_projects(group_name)
        logger.info(f"Retrieved {len(self.stored_projects)} projects.")

    # save data to sqlite db using pandas to_sql
    def save_data(self):
        logger.info("Saving data to database...")
        df = pd.DataFrame([project.__dict__ for project in self.stored_projects])
        # Add the following
        df['namespace'] = df['namespace'].apply(str)
        df.to_sql("projects", connect_to_db(), if_exists="replace", index=False)
        logger.info("Data saved to database.")

    def refresh_data(self, group_name):
        self.retrieve_data(group_name)
        self.save_data()
        logger.info(f"Data refreshed for group: {group_name}")

if __name__ == "__main__":

    ProjectsDataRetriever().refresh_data(group_name="test-group")
    df = pd.read_sql("select * from projects", connect_to_db())
    # print all columns and rows
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    print(df.head())