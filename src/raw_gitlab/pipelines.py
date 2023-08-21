from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import gitlab
from src.utils.database import connect_to_db
from src.utils.gitlab_connect import connect_to_gitlab
from src.utils.logger import setup_logger

logger = setup_logger("gitlab_logger", "gitlab_log.txt")

@dataclass
class Pipeline:
    iid: int
    project_id: int
    status: str
    source: str
    ref: str
    sha: str
    web_url: str
    created_at: datetime
    updated_at: datetime



class PipelinesDataRetriever:
    stored_pipelines = []  # This will store the pipelines data

    def __init__(self):
        self.gl = connect_to_gitlab()

    def get_all_pipelines(self, group_name):
        group = self.gl.groups.get(group_name)
        gitlab_projects = group.projects.list(all=True, include_subgroups=True)

        for project in gitlab_projects:
            full_project = self.gl.projects.get(project.id)
            try:
                gitlab_pipelines = full_project.pipelines.list(all=True)
            except gitlab.exceptions.GitlabListError as e:
                logger.warning(f"Failed to retrieve pipelines for project {project.id}: {e}")
                continue

            for pipeline in gitlab_pipelines:
                # rest of the code remains unchanged

                pipe = Pipeline(
                    iid=pipeline.iid,
                    project_id=project.id,
                    status=pipeline.status,
                    source=pipeline.source,
                    ref=pipeline.ref,
                    sha=pipeline.sha,
                    web_url=pipeline.web_url,
                    created_at=datetime.strptime(pipeline.created_at, '%Y-%m-%dT%H:%M:%S.%fZ'),
                    updated_at=datetime.strptime(pipeline.updated_at, '%Y-%m-%dT%H:%M:%S.%fZ')
                )
                self.stored_pipelines.append(pipe)  # Store the data in the class variable

    def retrieve_data(self, group_name):
        logger.info("Starting pipeline data retrieval...")
        self.get_all_pipelines(group_name)
        logger.info(f"Retrieved {len(self.stored_pipelines)} pipelines.")

    # save data to sqlite db using pandas to_sql
    def save_data(self):
        logger.info("Saving data to database...")
        df = pd.DataFrame([pipeline.__dict__ for pipeline in self.stored_pipelines])
        df.to_sql('pipelines', con=connect_to_db(), if_exists='replace', index=False)
        logger.info("Data saved to database.")
 
    def refresh_data(self, group_name):
        self.retrieve_data(group_name)
        self.save_data()
        logger.info(f"Data refreshed for group: {group_name}")

if __name__ == "__main__":
    from dotenv import find_dotenv, load_dotenv
    load_dotenv(find_dotenv())
    import os

    PipelinesDataRetriever().refresh_data(group_name=os.getenv('GITLAB_GROUP'))
    df = pd.read_sql("select * from pipelines", connect_to_db())
    print(df.head())