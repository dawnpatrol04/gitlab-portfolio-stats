from raw_gitlab.projects import ProjectsDataRetriever, logger  # Assuming these are defined in projects.py
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

from utils.database import connect_to_db
from datetime import datetime, timedelta
from collections import OrderedDict

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

            # Attempt to fetch the email using the emails attribute
            email = ""
            try:
                user_emails = user.emails.list()
                email = user_emails[0].email if user_emails else ""
            except Exception as e:
                logger.warning(f"Could not retrieve email for user {user.username}. Error: {e}")

            # Check if 'created_at' field is populated
            if user.created_at:
                try:
                    usr = User(
                        id=user.id,
                        name=user.name,
                        username=user.username,
                        email=email,  # Use the fetched email here
                        state=user.state,
                        avatar_url=user.avatar_url,
                        web_url=user.web_url,
                        created_at=datetime.strptime(user.created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
                    )
                    self.stored_users.append(usr)
                except ValueError as e:
                    logger.warning(f"Invalid date format for user {user.username}. Error: {e}")
            else:
                logger.warning(f"User {user.username} does not have a populated 'created_at' field.")

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

    UsersDataRetriever().refresh_data(group_name="test-group")
    df = pd.read_sql("select * from users", connect_to_db())
    print(df.head())