from dataclasses import dataclass
from datetime import datetime
from utils.logger import setup_logger
from utils.gitlab_connect import connect_to_gitlab

from datetime import datetime, timedelta
from collections import OrderedDict , defaultdict
from calendar import month_name
from typing import List, Dict



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

class GitLabPipelineDataRetriever:
    stored_pipelines = []  # This will store the pipelines data

    def __init__(self):
        self.gl = connect_to_gitlab()

    def get_all_pipelines(self, group_name):
        group = self.gl.groups.get(group_name)
        gitlab_projects = group.projects.list(all=True, include_subgroups=True)
        
        for project in gitlab_projects:
            full_project = self.gl.projects.get(project.id)
            gitlab_pipelines = full_project.pipelines.list(all=True)
            
            for pipeline in gitlab_pipelines:
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

def get_pipeline_count_per_month(pipelines):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=6*30)  # Approximation for 6 months
    
    # Initialize an ordered dictionary with zeros for all months in the range
    monthly_counts = OrderedDict()
    for month_offset in range(6, -1, -1):
        month_year = (end_date - timedelta(days=30*month_offset)).strftime('%B %Y')
        monthly_counts[month_year] = 0

    # Update counts based on the pipelines' data
    for pipeline in pipelines:
        if start_date <= pipeline.created_at <= end_date:
            month_year = pipeline.created_at.strftime('%B %Y')
            monthly_counts[month_year] += 1

    return monthly_counts



def get_pipelines_by_source_per_month(pipelines):
    # Prepare an empty result dictionary
    result = {}
    
    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Calculate the last six months, taking into account the change of the year
    last_six_months = [(current_month - i + 12) % 12 or 12 for i in range(6)]
    last_six_month_names = [month_name[month] for month in reversed(last_six_months)]

    # Process each pipeline
    for pipeline in pipelines:
        source = pipeline.source
        created_month = month_name[pipeline.created_at.month]

        if source not in result:
            result[source] = {month: 0 for month in last_six_month_names}

        if created_month in last_six_month_names:
            result[source][created_month] += 1

    return result

def get_pipelines_by_source_percentage(pipelines ) -> Dict[str, float]:
    """
    Get the percentage of pipelines by source.
    """
    source_counts = defaultdict(int)

    # Calculate the total count for each source
    for pipeline in pipelines:
        source = pipeline.source
        source_counts[source] += 1

    # Calculate the total number of pipelines
    total_pipelines = sum(source_counts.values())

    # Calculate the percentage for each source
    percentages = {}
    for source, count in source_counts.items():
        if total_pipelines > 0:
            percentages[source] = (count / total_pipelines) * 100
        else:
            percentages[source] = 0

    return percentages


if __name__ == "__main__":
    retriever = GitLabPipelineDataRetriever()
    retriever.retrieve_data("test-group")
    print(GitLabPipelineDataRetriever.stored_pipelines)  # Print the stored pipelines





if __name__ == "__main__":
    retriever = GitLabPipelineDataRetriever()
    retriever.retrieve_data("test-group")
    print(GitLabPipelineDataRetriever.stored_pipelines)  # Print the stored pipelines
