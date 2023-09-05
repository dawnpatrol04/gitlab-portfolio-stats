import json
import os
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
from dotenv import find_dotenv, load_dotenv

from src.utils.database import connect_to_db
from src.utils.gitlab_connect import connect_to_gitlab
from src.utils.logger import setup_logger

load_dotenv(find_dotenv())
logger = setup_logger("gitlab_logger", "gitlab_log.txt")

@dataclass
class Commit:
    id: str
    short_id: str
    title: str
    author_name: str
    author_email: str
    authored_date: datetime
    committer_name: str
    committer_email: str
    committer_date: datetime  # Added this line
    created_at: datetime
    message: str
    parent_ids: str
    web_url: str
    
class CommitsDataRetriever:
    stored_commits = []  # This will store the commits data

    def __init__(self):
        self.gl = connect_to_gitlab()

    def get_all_commits(self, group_name):
        group = self.gl.groups.get(group_name)
        gitlab_projects = group.projects.list(all=True, include_subgroups=True)

        for project in gitlab_projects:
            full_project = self.gl.projects.get(project.id)
            gitlab_commits = full_project.commits.list(all=True)

            for commit in gitlab_commits:
                com = Commit(
                    id=commit.id,
                    short_id=commit.short_id,
                    title=commit.title,
                    author_name=commit.author_name,
                    author_email=commit.author_email,
                    authored_date=datetime.fromisoformat(commit.authored_date),
                    committer_name=commit.committer_name,
                    committer_email=commit.committer_email,
                    committer_date=datetime.fromisoformat(commit.committed_date),
                    created_at=datetime.fromisoformat(commit.created_at),
                    message=commit.message,
                    parent_ids=json.dumps(commit.parent_ids), 
                    web_url=commit.web_url
                )
                self.stored_commits.append(com)  # Store the data in the class variable

    def retrieve_data(self, group_name):
        logger.info("Starting commit data retrieval...")
        self.get_all_commits(group_name)
        logger.info(f"Retrieved {len(self.stored_commits)} commits.")

    def save_data(self):
        logger.info("Saving data to database...")
        df = pd.DataFrame([commit.__dict__ for commit in self.stored_commits])  # Note the change here
        df.to_sql("commits", connect_to_db(), if_exists="replace", index=False)
        logger.info("Data saved to database.")
    
    #  refresh data
    def refresh_data(self, group_name):
        self.retrieve_data(group_name)
        self.save_data()
        logger.info(f"Data refreshed for group: {group_name}")
 
if __name__ == "__main__":
 
    CommitsDataRetriever().refresh_data(group_name=os.getenv('GITLAB_GROUP'))
    df = pd.read_sql("select * from commits", connect_to_db())
    print(df.head())
