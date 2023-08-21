from fastapi import APIRouter 
import pandas as pd
from utils.database import connect_to_db


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

