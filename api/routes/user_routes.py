from fastapi import APIRouter 
import pandas as pd
from utils.database import connect_to_db 

router = APIRouter()

 
# User Routes
@router.get("/users/", tags=["users"])
def list_users():
    df = pd.read_sql("SELECT * FROM users", connect_to_db())
    return df.to_dict(orient='records')

@router.get("/users/count/", tags=["users"])
def count_users():
    df = pd.read_sql("SELECT * FROM users", connect_to_db())
    return {"user_count": len(df)}

@router.get("/users/count-per-month/", tags=["users"])
def users_per_month():
    df = pd.read_sql('''SELECT strftime('%Y-%m', created_at) AS month_year, COUNT(*) AS user_count
                        FROM users
                        GROUP BY month_year
                        ORDER BY month_year''', connect_to_db())
    labels = df["month_year"].tolist()
    data_values = df["user_count"].tolist()
    return {
        "labels": labels,
        "data": data_values
    }
