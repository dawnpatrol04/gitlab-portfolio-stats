from dataclasses import dataclass
from datetime import datetime
from utils.logger import setup_logger
from utils.gitlab_connect import connect_to_gitlab

from datetime import datetime, timedelta
from collections import OrderedDict


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
    parent_ids: list
    web_url: str
    
class GitLabCommitDataRetriever:
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
                    parent_ids=commit.parent_ids,
                    web_url=commit.web_url
                )
                self.stored_commits.append(com)  # Store the data in the class variable

    def retrieve_data(self, group_name):
        logger.info("Starting commit data retrieval...")
        self.get_all_commits(group_name)
        logger.info(f"Retrieved {len(self.stored_commits)} commits.")

def get_commit_count_per_month(commits):
    end_date = datetime.now().astimezone(None)  # Make timezone-naive
    start_date = (end_date - timedelta(days=15*30)).astimezone(None)  # Make timezone-naive


    # Initialize an ordered dictionary with zeros for all months in the range
    monthly_counts = OrderedDict()
    for month_offset in range(15, -1, -1):
        month_year = (end_date - timedelta(days=30*month_offset)).strftime('%B %Y')
        monthly_counts[month_year] = 0

    # Update counts based on the commits' data
    for commit in commits:
        if start_date <= commit.created_at <= end_date:
            month_year = commit.created_at.strftime('%B %Y')
            monthly_counts[month_year] += 1

    return monthly_counts

if __name__ == "__main__":
    retriever = GitLabCommitDataRetriever()
    retriever.retrieve_data("test-group")
    print(GitLabCommitDataRetriever.stored_commits)  # Print the stored commits
