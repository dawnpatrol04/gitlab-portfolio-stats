from fastapi import APIRouter 

from datetime import datetime
import pandas as pd
from src.utils.database import connect_to_db

router = APIRouter()

  


# Commit Routes
@router.get("/commits/", tags=["commits"])
def list_commits():
    df = pd.read_sql("SELECT * FROM commits", connect_to_db())
    return df.to_dict(orient='records')

@router.get("/commits/count/", tags=["commits"])
def count_commits():
    df = pd.read_sql("SELECT * FROM commits", connect_to_db())
    return {"commit_count": len(df)}


@router.get("/commits/count-per-month/", tags=["commits"])
def commits_per_month(start_month: str = "2022-01"):
    # Generate the complete list of months from start_month to the current month
    current_month = datetime.now().strftime('%Y-%m')
    all_months = pd.date_range(start_month, current_month, freq='MS').strftime('%Y-%m').tolist()

    df = pd.read_sql('''SELECT strftime('%Y-%m', authored_date) AS month_year, COUNT(*) AS commit_count
                        FROM commits
                        WHERE strftime('%Y-%m', authored_date) >= ?
                        GROUP BY month_year
                        ORDER BY month_year''', connect_to_db(), params=(start_month,))

    # Convert fetched data to dictionary for easy lookup
    fetched_data = dict(zip(df["month_year"], df["commit_count"]))

    # Ensure every month has a corresponding count
    labels = []
    data_values = []
    for month in all_months:
        labels.append(month)
        data_values.append(fetched_data.get(month, 0))

    return {
        "labels": labels,
        "data": data_values
    }

