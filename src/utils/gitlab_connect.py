import gitlab
import os
from dotenv import load_dotenv, find_dotenv

def connect_to_gitlab():
    # Load environment variables, ideally from a .env file
    load_dotenv(find_dotenv())
    
    # Fetch GitLab URL and Token from the environment
    gl_url = os.getenv('GITLAB_URL')
    gl_token = os.getenv('GITLAB_TOKEN')
    
    # Ensure that the required environment variables are set
    if not all([gl_url, gl_token]):
        raise EnvironmentError("GITLAB_URL and GITLAB_TOKEN must be set in the environment or in a .env file.")
    
    # Connect and authenticate with GitLab using the provided URL and token
    gl = gitlab.Gitlab(gl_url, private_token=gl_token, keep_base_url=True)

    # Optional: You can test the connection by fetching the current user's details
    # gl.user.get_current()
    
    return gl

if __name__ == '__main__':
    gl = connect_to_gitlab()
