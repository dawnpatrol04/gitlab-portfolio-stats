from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd

from src.raw_gitlab.projects import  ProjectsDataRetriever, logger 
from src.utils.database import connect_to_db


@dataclass
class User:
    id: int
    name: str
    username: str
    email: str
    state: str
    avatar_url: str
    web_url: str
    created_at: datetime

class UsersDataRetriever(ProjectsDataRetriever):
    stored_users = []

    def get_all_users(self, group_name):
        group = self.gl.groups.get(group_name)  # Get the specified group
        members = group.members.list(all=True, include_subgroups=True)  # Fetch all members, including those from subgroups

        for member in members:
            user = self.gl.users.get(member.id)
            email = ""
            try:
                user_emails = user.emails.list()
                email = user_emails[0].email if user_emails else ""
            except Exception as e:
                logger.warning(f"Could not retrieve email for user {user.username}. Error: {e}")
            try:
                created_date = datetime.strptime(user.created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
            except AttributeError:
                logger.warning(f"'User' object {user.id} ({user.username}) has no attribute 'created_at'. Skipping.")
                continue
            except ValueError as e:
                logger.warning(f"Invalid date format for user {user.username}. Error: {e}")
                continue

            usr = User(
                id=user.id,
                name=user.name,
                username=user.username,
                email=email,
                state=user.state,
                avatar_url=user.avatar_url,
                web_url=user.web_url,
                created_at=created_date
            )
            self.stored_users.append(usr)

    def retrieve_user_data(self, group_name="default_group_name"):
        logger.info("Starting user data retrieval...")
        self.get_all_users(group_name)  # Pass the group name here
        logger.info(f"Retrieved {len(self.stored_users)} users.")
        return self.stored_users

    def save_data(self):
        logger.info("Saving data to database...")
        df = pd.DataFrame([user.__dict__ for user in self.stored_users])
        print(df)
        if not df.empty:
            df['created_at'] = df['created_at'].apply(str)
            df.to_sql("users", connect_to_db(), if_exists="replace", index=False)
        logger.info("Data saved to database.")

    def refresh_data(self, group_name):
        self.retrieve_user_data(group_name)  # Update this line
        self.save_data()
        logger.info(f"Data refreshed for group: {group_name}")


if __name__ == "__main__":
    from dotenv import find_dotenv, load_dotenv
    load_dotenv(find_dotenv())
    import os

    UsersDataRetriever().refresh_data(group_name=os.getenv('GITLAB_GROUP'))
    df = pd.read_sql("select * from users", connect_to_db())
    print(df.head())