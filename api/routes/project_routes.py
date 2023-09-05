from fastapi import APIRouter 
import pandas as pd
from src.utils.database import connect_to_db
from src.raw_gitlab.project_file_data import process_and_enrich_gitlab_data

from datetime import datetime

router = APIRouter()

# Project Routes
@router.get("/projects/", tags=["projects"])
def list_projects():
    df = pd.read_sql("SELECT * FROM projects", connect_to_db())
    return df.to_dict(orient='records')

@router.get("/projects/count/", tags=["projects"])
def count_unique_projects():
    df = pd.read_sql("SELECT * FROM projects", connect_to_db())
    return {"project_count": len(df)}

@router.get("/projects/count-per-month/", tags=["projects"])
def projects_per_month():
    df = pd.read_sql('''SELECT strftime('%Y-%m', created_at) AS month_year, COUNT(*) AS project_count
                        FROM projects
                        GROUP BY month_year
                        ORDER BY month_year''', connect_to_db())
    labels = df["month_year"].tolist()
    data_values = df["project_count"].tolist()
    return {
        "labels": labels,
        "data": data_values
    }

@router.get("/projects/details/", tags=["projects"])
def project_details():
    query = '''
        SELECT 
            p.id AS project_id,
            p.name AS project_name,
            p.description,
            p.visibility,
            p.web_url,
            p.open_issues_count,
            p.last_activity_at,
            COUNT(DISTINCT pl.iid) AS pipeline_count,
            COUNT(DISTINCT c.id) AS commit_count,
            u.name AS creator_name 
        FROM projects p
        LEFT JOIN pipelines pl ON p.id = pl.project_id
        LEFT JOIN commits c ON p.id = c.id -- Assuming a relationship exists
        LEFT JOIN users u ON p.creator_id = u.id
        GROUP BY p.id;
    '''
    df = pd.read_sql(query, connect_to_db())
    
    # Convert the dataframe to a dictionary for returning as JSON
    result = df.to_dict(orient="records")

    return result


@router.post("/projects/process-and-enrich/", tags=["projects"])
def process_and_enrich_data():
    """Trigger processing and enrichment of GitLab data."""
    try:
        process_and_enrich_gitlab_data()
        return {"status": "success", "message": "GitLab data processed and enriched successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}