from fastapi import APIRouter, Depends, HTTPException

from datetime import datetime, timedelta
from collections import OrderedDict

from retrievers.projects import GitLabDataRetriever, get_project_count_per_month, Project
from retrievers.users import UserDataRetriever,get_users_count_per_month, User
from retrievers.pipelines import GitLabPipelineDataRetriever, get_pipeline_count_per_month, get_pipelines_by_source_per_month, get_pipelines_by_source_percentage, Pipeline  # import necessary classes from pipelines.py
from retrievers.commits import GitLabCommitDataRetriever, get_commit_count_per_month, Commit  # Make sure to import the necessary classes from commits.py

router = APIRouter()

# Dependencies
def get_project_data_retriever():
    return GitLabDataRetriever()

def get_user_data_retriever():
    return UserDataRetriever()

def get_pipeline_data_retriever():
    return GitLabPipelineDataRetriever()

def get_commit_data_retriever():
    return GitLabCommitDataRetriever()  # Dependency for commit data retriever

# run this when the server starts to get the data
@router.on_event("startup")
@router.post("/refresh-all/", tags=["general"])
def refresh_all_data(group_name: str = "test-group"):
    project_retriever = get_project_data_retriever()
    user_retriever = get_user_data_retriever()
    pipeline_retriever = get_pipeline_data_retriever()
    commit_retriever = get_commit_data_retriever()

    try:
        project_retriever.retrieve_data(group_name)
        user_retriever.retrieve_user_data(group_name)
        pipeline_retriever.retrieve_data(group_name)
        commit_retriever.retrieve_data(group_name)

        return {"message": f"All data refreshed for group: {group_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Project Routes ################################################################
@router.post("/projects/refresh/", tags=["projects"])
def refresh_project_data(group_name: str = "test-group", retriever: GitLabDataRetriever = Depends(get_project_data_retriever)):
    try:
        retriever.retrieve_data(group_name)
        return {"message": f"Project data refreshed for group: {group_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/", tags=["projects"])
def list_projects():
    return GitLabDataRetriever.stored_projects

@router.get("/projects/count/", tags=["projects"])
def count_unique_projects():
    unique_project_ids = {project.id for project in GitLabDataRetriever.stored_projects}
    return {"project_count": len(unique_project_ids)}

@router.get("/projects/count-per-month/", tags=["projects"])
def count_projects_per_month():
    project_counts = get_project_count_per_month(GitLabDataRetriever.stored_projects)
    labels = list(project_counts.keys())
    data_values = list(project_counts.values())
    return {
        "labels": labels,
        "data": data_values
    }


# User Routes ################################################################
@router.post("/users/refresh/", tags=["users"])
def refresh_user_data(group_name: str = "test-group", retriever: UserDataRetriever = Depends(get_user_data_retriever)):
    try:
        retriever.retrieve_user_data(group_name)
        return {"message": f"User data refreshed for group: {group_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/", tags=["users"])
def list_users():
    return UserDataRetriever.stored_users

@router.get("/users/count/", tags=["users"])
def count_users():
    return {"user_count": len(UserDataRetriever.stored_users)}

@router.get("/users/count-per-month/", tags=["users"])
def count_users_per_month():
    user_counts = get_users_count_per_month(UserDataRetriever.stored_users)
    labels = list(user_counts.keys())
    data_values = list(user_counts.values())
    return {
        "labels": labels,
        "data": data_values
    }



 # Pipeline Routes ################################################################
@router.post("/pipelines/refresh/", tags=["pipelines"])
def refresh_pipeline_data(group_name: str = "test-group", retriever: GitLabPipelineDataRetriever = Depends(get_pipeline_data_retriever)):
    try:
        retriever.retrieve_data(group_name)
        return {"message": f"Pipeline data refreshed for group: {group_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pipelines/", tags=["pipelines"])
def list_pipelines():
    return GitLabPipelineDataRetriever.stored_pipelines

@router.get("/pipelines/count/", tags=["pipelines"])
def count_pipelines():
    return {"pipeline_count": len(GitLabPipelineDataRetriever.stored_pipelines)}

@router.get("/pipelines/count-per-month/", tags=["pipelines"])
def count_pipelines_per_month():
    pipeline_counts = get_pipeline_count_per_month(GitLabPipelineDataRetriever.stored_pipelines)
    labels = list(pipeline_counts.keys())
    data_values = list(pipeline_counts.values())
    return {
        "labels": labels,
        "data": data_values
    }

@router.get("/pipelines/by-source-per-month/", tags=["pipelines"])
def pipelines_by_source_per_month():
    data = get_pipelines_by_source_per_month(GitLabPipelineDataRetriever.stored_pipelines)
    return data

@router.get("/pipelines/by-source-percentage/", tags=["pipelines"])
def get_pipeline_percentage_by_source():
    return get_pipelines_by_source_percentage(GitLabPipelineDataRetriever.stored_pipelines)


# Commit Routes ################################################################
@router.post("/commits/refresh/", tags=["commits"])
def refresh_commit_data(group_name: str = "test-group", retriever: GitLabCommitDataRetriever = Depends(get_commit_data_retriever)):
    try:
        retriever.retrieve_data(group_name)
        return {"message": f"Commit data refreshed for group: {group_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/commits/", tags=["commits"])
def list_commits():
    return GitLabCommitDataRetriever.stored_commits

@router.get("/commits/count/", tags=["commits"])
def count_commits():
    return {"commit_count": len(GitLabCommitDataRetriever.stored_commits)}

@router.get("/commits/count-per-month/", tags=["commits"])
def count_commits_per_month():
    commit_counts = get_commit_count_per_month(GitLabCommitDataRetriever.stored_commits)
    labels = list(commit_counts.keys())
    data_values = list(commit_counts.values())
    
    return {
        "labels": labels,
        "data": data_values
    }