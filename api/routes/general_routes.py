import os

import pandas as pd
from dotenv import find_dotenv, load_dotenv
from fastapi import APIRouter, Depends, HTTPException

from src.raw_gitlab.commits import CommitsDataRetriever
from src.raw_gitlab.pipelines import PipelinesDataRetriever
from src.raw_gitlab.projects_v2 import 
from src.raw_gitlab.users import UsersDataRetriever
from src.utils.database import connect_to_db
# from src.raw_gitlab.projects_v2 import refresh_gitlab_data

load_dotenv(find_dotenv())
router = APIRouter()

def insert_or_update_sqlite(table_name: str, data: list[dict]):
    df = pd.DataFrame(data)
    with connect_to_db() as conn:
        df.to_sql(table_name, conn, if_exists='replace', index=False)


@router.post("/refresh-all/", tags=["general"])
def refresh_all_hybrid(group_name: str = os.getenv('GITLAB_GROUP')):
    CommitsDataRetriever().refresh_data(group_name=group_name)
    PipelinesDataRetriever().refresh_data(group_name=group_name)
    # ProjectsDataRetriever().refresh_data(group_name=group_name)
    UsersDataRetriever().refresh_data(group_name=group_name)
    # refresh_gitlab_data(group_name=group_name)
    return {"message": "Data refreshed successfully."}

