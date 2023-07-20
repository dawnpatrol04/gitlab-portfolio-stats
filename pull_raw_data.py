import gitlab
import os
from dotenv import load_dotenv, find_dotenv
import csv

def connect_to_gitlab():
    # load environment variables GITLAB-TOKEN and GITLAB_URL
    load_dotenv(find_dotenv())
    gl_url = os.getenv('GITLAB_URL')
    gl_token = os.getenv('GITLAB_TOKEN')
    # private token authentication
    gl = gitlab.Gitlab(gl_url, private_token=gl_token)
    return gl

def get_all_projects(gl, group_name):
    # Get all projects that the authenticated user has access to
    group = gl.groups.get( group_name )
    all_projects = group.projects.list(all=True , include_subgroups=True)
    return all_projects

def get_project_data(all_projects):
    # List of example projects
    example_projects = [
        "fpas_colab/mlops/cyberark",
        "fpas_colab/one-forecast-apps/cicd_test_1f",
        "fpas_colab/mlops/scrape",
        "fpas_colab/playground/test-project",
        "fpas_colab/mlops/gr_test_2",
        "fpas_colab/mlops/gr_test",
        "fpas_colab/playground/venv_demo",
        "fpas_colab/examples/cicd-dev-jami",
        "fpas_colab/mlops/multi-branch-pipeline-for-web-applications",
        "fpas_colab/examples/healthcheck-streamlit-example",
        "fpas_colab/mlops/blueprint-streamlit",
        "fpas_colab/mlops/cicd_dev",
        "fpas_colab/mlops/cicd_v2",
        "fpas_colab/examples/example_project",
        "fpas_colab/mlops/aj_test_project",
    ]

    project_data = []
    for project in all_projects:
        project_data.append({
            "id": project.id,
            "description": project.description,
            "default_branch": project.default_branch,
            "visibility": project.visibility,
            "ssh_url_to_repo": project.ssh_url_to_repo,
            "http_url_to_repo": project.http_url_to_repo,
            "web_url": project.web_url,
            "name": project.name,
            "name_with_namespace": project.name_with_namespace,
            "path": project.path,
            "path_with_namespace": project.path_with_namespace,
            "issues_enabled": project.issues_enabled,
            "open_issues_count": project.open_issues_count,
            "jobs_enabled": project.jobs_enabled,
            "wiki_enabled": project.wiki_enabled,
            "snippets_enabled": project.snippets_enabled,
            "resolve_outdated_diff_discussions": project.resolve_outdated_diff_discussions,
            "container_registry_enabled": project.container_registry_enabled,
            "created_at": project.created_at,
            "last_activity_at": project.last_activity_at,
            "creator_id": project.creator_id,
            "namespace": project.namespace,
            "import_status": project.import_status,
            "archived": project.archived,
            "avatar_url": project.avatar_url,
            "shared_runners_enabled": project.shared_runners_enabled,
            "marked_for_deletion_at": project.marked_for_deletion_at,
            "is_example_project": project.path_with_namespace in example_projects,  # New field
        })
    return project_data

def get_pipeline_data(gl, project):
    try:
        # Retrieve the full project data
        full_project = gl.projects.get(project.id)
        # Get all pipelines for the project
        pipelines = full_project.pipelines.list(all=True)
        pipeline_data = []
        for pipeline in pipelines:
            pipeline_data.append({
                "iid": pipeline.iid,
                "Project ID": project.id,
                "status": pipeline.status,
                "source": pipeline.source,
                "ref": pipeline.ref,
                "sha": pipeline.sha,
                # "name": pipeline.name,
                "web_url": pipeline.web_url,
                "created_at": pipeline.created_at,
                "updated_at": pipeline.updated_at
            })
    except gitlab.exceptions.GitlabListError as e:
        print(f"Could not fetch pipelines for project {project.id}. Error: {e}")
        pipeline_data = []  # Return an empty list when an error occurs
    return pipeline_data

def get_commit_data(gl, project):
    try:
        # Retrieve the full project data
        full_project = gl.projects.get(project.id)
        # Get all commits for the project
        commits = full_project.commits.list(all=True)
        commit_data = []
        for commit in commits:
            commit_data.append({
                "id": commit.id,
                "short_id": commit.short_id,
                "title": commit.title,
                "author_name": commit.author_name,
                "author_email": commit.author_email,
                "authored_date": commit.authored_date,
                "committer_name": commit.committer_name,
                "committer_email": commit.committer_email,
                "committed_date": commit.committed_date,
                "created_at": commit.created_at,
                "message": commit.message,
                "parent_ids": commit.parent_ids,
                "web_url": commit.web_url
            })
    except gitlab.exceptions.GitlabListError as e:
        print(f"Could not fetch commits for project {project.id}. Error: {e}")
        commit_data = []  # Return an empty list when an error occurs
    return commit_data

def get_pipeline_schedule_data(gl, project):
    try:
        # Retrieve the full project data
        full_project = gl.projects.get(project.id)
        # Get all pipeline schedules for the project
        schedules = full_project.pipelineschedules.list(all=True)
        schedule_data = []
        for schedule in schedules:
            owner = schedule.owner
            schedule_data.append({
                "id": schedule.id,
                "description": schedule.description,
                "ref": schedule.ref,
                "cron": schedule.cron,
                "cron_timezone": schedule.cron_timezone,
                "next_run_at": schedule.next_run_at,
                "active": schedule.active,
                "created_at": schedule.created_at,
                "updated_at": schedule.updated_at,
                "owner_name": owner['name'],
                "owner_username": owner['username'],
                "owner_id": owner['id'],
                "owner_state": owner['state'],
                "owner_avatar_url": owner['avatar_url'],
                "owner_web_url": owner['web_url']
            })
    except gitlab.exceptions.GitlabListError as e:
        print(f"Could not fetch pipeline schedules for project {project.id}. Error: {e}")
        schedule_data = []  # Return an empty list when an error occurs
    return schedule_data

def get_runner_data(gl, project):
    try:
        # Retrieve the full project data
        full_project = gl.projects.get(project.id)
        # Get all runners for the project
        runners = full_project.runners.list()
        runner_data = []
        for runner in runners:
            runner_data.append({
                "id": runner.id,
                "description": runner.description,
                "ip_address": runner.ip_address,
                "active": runner.active,
                "is_shared": runner.is_shared,
                "runner_type": runner.runner_type,
                "online": runner.online,
                "status": runner.status,
                "paused": runner.paused,
                "name": runner.name
            })
    except gitlab.exceptions.GitlabListError as e:
        print(f"Could not fetch runners for project {project.id}. Error: {e}")
        runner_data = []  # Return an empty list when an error occurs
    return runner_data

def get_gitlab_ci_file_content(project, branch_name):
    try:
        # Specify file path
        file_path = '.gitlab-ci.yml'

        # Get file from repository
        file = project.files.get(file_path=file_path, ref=branch_name)

        # Get file content
        file_content = file.decode()

        return file_content
    except gitlab.exceptions.GitlabGetError:
        # File does not exist
        return ''
    
def get_jenkins_file_content(project, branch_name):
    try:
        # Specify file path
        file_path = 'Jenkinsfile'

        # Get file from repository
        file = project.files.get(file_path=file_path, ref=branch_name)

        # Get file content
        file_content = file.decode()

        return file_content
    except gitlab.exceptions.GitlabGetError:
        # File does not exist
        return ''

def get_branch_data(gl, project):
    try:
        full_project = gl.projects.get(project.id)
        branches = full_project.branches.list(all=True)
        branch_data = []
        for branch in branches:
            commit = branch.commit
            gitlab_ci_file_content = get_gitlab_ci_file_content(gl, full_project, branch.name)
            jenkins_file_content = get_jenkins_file_content(full_project, branch.name)
            branch_data.append({
                "name": branch.name,
                "merged": branch.merged,
                "protected": branch.protected,
                "default": branch.default,
                "developers_can_push": branch.developers_can_push,
                "developers_can_merge": branch.developers_can_merge,
                "can_push": branch.can_push,
                "web_url": branch.web_url,
                "commit_author_email": commit['author_email'],
                "commit_author_name": commit['author_name'],
                "commit_authored_date": commit['authored_date'],
                "commit_committed_date": commit['committed_date'],
                "commit_committer_email": commit['committer_email'],
                "commit_committer_name": commit['committer_name'],
                "commit_id": commit['id'],
                "commit_short_id": commit['short_id'],
                "commit_title": commit['title'],
                "commit_message": commit['message'],
                "commit_parent_ids": commit['parent_ids'],
                "gitlab-ci.yml content": gitlab_ci_file_content,  # Existing field
                "Jenkinsfile content": jenkins_file_content  # New field
            })
    except gitlab.exceptions.GitlabListError as e:
        print(f"Could not fetch branches for project {project.id}. Error: {e}")
        branch_data = []  # Return an empty list when an error occurs
    return branch_data

 
def get_job_data(gl, project):
    try:
        full_project = gl.projects.get(project.id)
        jobs = full_project.jobs.list(all=True)
        job_data = []
        for job in jobs:
            job_data.append({
                "id": job.id,
                "status": job.status,
                "stage": job.stage,
                "name": job.name,
                "ref": job.ref,
                "tag": job.tag,
                "web_url": job.web_url,
                "duration": job.duration
            })
    except gitlab.exceptions.GitlabListError as e:
        print(f"Could not fetch jobs for project {project.id}. Error: {e}")
        job_data = []  # Return an empty list when an error occurs
    return job_data
 
def get_project_members(gl, project):
    try:
        full_project = gl.projects.get(project.id)
        members = full_project.members.list(all=True)
        member_data = []
        for member in members:
            member_data.append({
                "id": member.id,
                "username": member.username,
                "name": member.name,
                "state": member.state,
                "access_level": member.access_level,
                "expires_at": member.expires_at,
                "web_url": member.web_url
            })
    except gitlab.exceptions.GitlabListError as e:
        print(f"Could not fetch members for project {project.id}. Error: {e}")
        member_data = []  # Return an empty list when an error occurs
    return member_data
 
def get_merge_request_data(gl, project):
    try:
        full_project = gl.projects.get(project.id)
        merge_requests = full_project.mergerequests.list(all=True)
        merge_request_data = []
        for merge_request in merge_requests:
            merge_request_data.append({
                "id": merge_request.id,
                "title": merge_request.title,
                "description": merge_request.description,
                "state": merge_request.state,
                "created_at": merge_request.created_at,
                "updated_at": merge_request.updated_at,
                "merged_by": merge_request.merged_by,
                "merged_at": merge_request.merged_at,
                "closed_by": merge_request.closed_by,
                "closed_at": merge_request.closed_at,
                "target_branch": merge_request.target_branch,
                "source_branch": merge_request.source_branch,
                "web_url": merge_request.web_url
            })
    except gitlab.exceptions.GitlabListError as e:
        print(f"Could not fetch merge requests for project {project.id}. Error: {e}")
        merge_request_data = []  # Return an empty list when an error occurs
    return merge_request_data
 
def get_project_tags(gl, project):
    try:
        full_project = gl.projects.get(project.id)
        tags = full_project.tags.list(all=True)
        tag_data = []
        for tag in tags:
            tag_data.append({
                "name": tag.name,
                "message": tag.message,
                "commit": tag.commit,
                "release": tag.release
            })
    except gitlab.exceptions.GitlabListError as e:
        print(f"Could not fetch tags for project {project.id}. Error: {e}")
        tag_data = []  # Return an empty list when an error occurs
    return tag_data

def write_data_to_csv(file_name, data):
    # Write data to CSV
    with open(file_name, 'w', newline='') as file:
        if data:  # Check if data is not empty
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        else:
            print(f"No data to write for {file_name}.")

if __name__ == "__main__":
    # Get all projects
    group_name = "fpas_colab"
    gl = connect_to_gitlab()
    all_projects = get_all_projects(gl, group_name)

    # Prepare data lists
    project_data = get_project_data(all_projects)
    pipeline_data = []
    commit_data = []
    schedule_data = []
    runner_data = []
    branch_data = []
    job_data = []
    member_data = []
    merge_request_data = []
    tag_data = []

    # Get data for each project
    for project in all_projects:
        pipeline_data = get_pipeline_data(gl, project)
        # commit_data = get_commit_data(gl, project)
        # schedule_data = get_pipeline_schedule_data(gl, project)
        # runner_data = get_runner_data(gl, project)
        # branch_data = get_branch_data(gl, project)
        # job_data = get_job_data(gl, project)
        # member_data = get_project_members(gl, project)
        # merge_request_data = get_merge_request_data(gl, project)
        # tag_data = get_project_tags(gl, project)

    # Write data to CSV files
    write_data_to_csv('projects.csv', project_data)
    write_data_to_csv('pipelines.csv', pipeline_data)
    write_data_to_csv('commits.csv', commit_data)
    write_data_to_csv('schedules.csv', schedule_data)
    write_data_to_csv('branches.csv', branch_data)
    write_data_to_csv('runners.csv', runner_data)
    write_data_to_csv('jobs.csv', job_data)
    write_data_to_csv('members.csv', member_data)
    write_data_to_csv('merge_requests.csv', merge_request_data)
    write_data_to_csv('tags.csv', tag_data)