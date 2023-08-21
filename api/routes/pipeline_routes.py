from fastapi import APIRouter 
import pandas as pd
from src.utils.database import connect_to_db
 

from datetime import datetime

router = APIRouter()

 
# Pipeline Routes
@router.get("/pipelines/", tags=["pipelines"])
def list_pipelines():
    df = pd.read_sql("SELECT * FROM pipelines", connect_to_db())
    return df.to_dict(orient='records')

@router.get("/pipelines/count/", tags=["pipelines"])
def count_pipelines():
    df = pd.read_sql("SELECT * FROM pipelines", connect_to_db())
    return {"pipeline_count": len(df)}

@router.get("/pipelines/count-per-month/", tags=["pipelines"])
def pipelines_per_month(start_month: str = "2022-01"):
    # Generate the complete list of months from start_month to the current month
    current_month = datetime.now().strftime('%Y-%m')
    all_months = pd.date_range(start_month, current_month, freq='MS').strftime('%Y-%m').tolist()

    df = pd.read_sql('''SELECT strftime('%Y-%m', created_at) AS month_year, COUNT(*) AS pipeline_count
                        FROM pipelines
                        WHERE strftime('%Y-%m', created_at) >= ?
                        GROUP BY month_year
                        ORDER BY month_year''', connect_to_db(), params=(start_month,))

    # Convert fetched data to dictionary for easy lookup
    fetched_data = dict(zip(df["month_year"], df["pipeline_count"]))

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

@router.get("/pipelines/by_source/", tags=["pipelines"])
def pipelines_by_source():
    df = pd.read_sql('SELECT source, COUNT(*) AS source_count FROM pipelines GROUP BY source', connect_to_db())
    return df.to_dict(orient='records')

@router.get("/pipelines/by-source-per-month/", tags=["pipelines"])
def pipelines_by_source_per_month(start_month: str = "2022-01"):
    # Generate the complete list of months from start_month to the current month
    current_month = datetime.now().strftime('%Y-%m')
    all_months = pd.date_range(start_month, current_month, freq='MS').strftime('%Y-%m').tolist()

    # Fetch data from the specified start_month onwards
    df = pd.read_sql('''SELECT source, strftime('%Y-%m', created_at) AS month_year, COUNT(*) AS pipeline_count
                        FROM pipelines
                        WHERE strftime('%Y-%m', created_at) >= ?
                        GROUP BY source, month_year
                        ORDER BY month_year, source''', connect_to_db(), params=(start_month,))

    # Convert fetched data to dictionary for easy lookup
    fetched_data = {(row["source"], row["month_year"]): row["pipeline_count"] for _, row in df.iterrows()}
    all_sources = df["source"].unique().tolist()

    # Prepare structured data for each source
    result_data = {}
    for source in all_sources:
        source_data = {}
        for month in all_months:
            source_data[month] = fetched_data.get((source, month), 0)
        result_data[source] = source_data

    return result_data




@router.get("/pipelines/by-source-percentage/", tags=["pipelines"])
def pipelines_by_source_percentage(start_date: str = "2022-01-01"):
    # Use the provided start_date in the SQL query
    df = pd.read_sql('''WITH total_pipelines AS (SELECT COUNT(*) as total FROM pipelines WHERE created_at >= ?)
                        SELECT source, (COUNT(*) * 100.0 / total) AS percentage
                        FROM pipelines, total_pipelines
                        WHERE pipelines.created_at >= ?
                        GROUP BY source''', connect_to_db(), params=(start_date, start_date))
    
    df['percentage'] = df['percentage'].round(2).astype(float)  # Round to 2 decimal places for cleaner output
    percentages_dict = dict(zip(df["source"], df["percentage"]))
    
    return percentages_dict

