from fastapi import APIRouter 
import pandas as pd
from utils.database import connect_to_db 

router = APIRouter()

from fastapi import APIRouter, Depends, HTTPException
import pandas as pd
from utils.database import connect_to_db
from raw_gitlab.projects import ProjectsDataRetriever
from raw_gitlab.users import UsersDataRetriever
from raw_gitlab.pipelines import PipelinesDataRetriever
from raw_gitlab.commits import CommitsDataRetriever

router = APIRouter()


def insert_or_update_sqlite(table_name: str, data: list[dict]):
    df = pd.DataFrame(data)
    with connect_to_db() as conn:
        df.to_sql(table_name, conn, if_exists='replace', index=False)


@router.post("/refresh-all/", tags=["general"])
def refresh_all_hybrid(group_name: str = "test-group"):
    CommitsDataRetriever().refresh_data(group_name=group_name)
    PipelinesDataRetriever().refresh_data(group_name=group_name)
    ProjectsDataRetriever().refresh_data(group_name=group_name)
    UsersDataRetriever().refresh_data(group_name=group_name)
    return {"message": "Data refreshed successfully."}

