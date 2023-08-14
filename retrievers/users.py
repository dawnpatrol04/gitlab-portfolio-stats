from retrievers.projects import GitLabDataRetriever, logger  # Assuming these are defined in projects.py
from dataclasses import dataclass
from datetime import datetime

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

class UserDataRetriever(GitLabDataRetriever):
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
        
    def retrieve_user_data(self, group_name="default_group_name"):
        logger.info("Starting user data retrieval...")
        self.get_all_users(group_name)  # Pass the group name here
        logger.info(f"Retrieved {len(self.stored_users)} users.")
        
def get_users_count_per_month(users):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=6*30)  # Approximation for 6 months
    
    # Initialize an ordered dictionary with zeros for all months in the range
    monthly_counts = OrderedDict()
    for month_offset in range(6, -1, -1):
        month_year = (end_date - timedelta(days=30*month_offset)).strftime('%B %Y')
        monthly_counts[month_year] = 0

    # Update counts based on the users' data
    for user in users:
        if start_date <= user.created_at <= end_date:
            month_year = user.created_at.strftime('%B %Y')
            monthly_counts[month_year] += 1

    return monthly_counts
if __name__ == "__main__":
    retriever = UserDataRetriever()
    retriever.retrieve_user_data(group_name= "test-group")  # Specify your group name here
    print(UserDataRetriever.stored_users)  # Print the stored users
