import gitlab
import pandas as pd
from dotenv import find_dotenv, load_dotenv

from src.utils.database import connect_to_db
from src.utils.gitlab_connect import connect_to_gitlab
from src.utils.logger import setup_logger

load_dotenv(find_dotenv())
logger = setup_logger("gitlab_logger", "gitlab_log.txt")


def is_serializable(value):
    """Check if the value is serializable."""
    serializable_types = (int, float, str, bool, type(None), list, dict)
    return isinstance(value, serializable_types)


def get_runner_attributes(runner):
    """Get all attributes of a runner object that can be serialized."""
    attributes = {}
    for attr in dir(runner):
        value = getattr(runner, attr)
        if not callable(value) and not attr.startswith("_") and is_serializable(value):
            if isinstance(value, list):
                if value and isinstance(value[0], dict):
                    # Convert each dictionary in the list to a string and then join them
                    attributes[attr] = '|'.join([str(item) for item in value])
                else:
                    # Join list into a string for simpler serialization
                    attributes[attr] = ','.join(map(str, value)) if value else None
            elif isinstance(value, dict):
                # Convert dict to a string representation
                attributes[attr] = str(value)
            else:
                attributes[attr] = value
    return attributes


def fetch_gitlab_runner_data():
    logger.info("Fetching runners from GitLab")
    gl = connect_to_gitlab()
    gitlab_runners = gl.runners.list(all=True)

    runners_list = []
    for runner in gitlab_runners:
        runner_detail = gl.runners.get(runner.id)  # Fetch detailed info for each runner
        runner_data = get_runner_attributes(runner_detail)
        runners_list.append(runner_data)

    logger.info("Finished fetching data for %d runners", len(runners_list))
    return pd.DataFrame(runners_list)


def save_runner_data_to_db(df):
    with connect_to_db() as conn:
        df.to_sql("runners", conn, if_exists="replace", index=False)


def refresh_runner_data():
    df = fetch_gitlab_runner_data()
    save_runner_data_to_db(df)
    return {"status": "success", "message": "Runner data refreshed successfully!"}


if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    refresh_runner_data()
    all_df = pd.read_sql("select * from runners", connect_to_db())
    print(all_df)
