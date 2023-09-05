import os

import numpy as np
import pandas as pd
from dotenv import find_dotenv, load_dotenv
from fastapi import APIRouter

# import src.raw_gitlab.projects_v2 as projects_v2
import src.utils.database as db

load_dotenv(find_dotenv())

router = APIRouter()

# @router.post("/refresh-gitlab-data/", tags=["projects_v2"])
# def refresh_gitlab_data(group_name: str = os.getenv('GITLAB_GROUP')):
#     df = projects_v2.fetch_gitlab_data(group_name)
#     projects_v2.save_data_to_db(df)
#     return {"status": "success", "message": f"Data for group {group_name} refreshed successfully!"}

# make a new route to return all the data from the table projects_v2
@router.get("/projects_v2/", tags=["projects_v2"])
def get_projects_v2():
    with db.connect_to_db() as conn:
        df = pd.read_sql("SELECT * FROM projects_v2", conn)
    
    # Explicitly replace NaN with None using numpy's nan
    df.replace({np.nan: None}, inplace=True)
    
    print(f"df: {df}")
    return df.to_dict(orient='records')
