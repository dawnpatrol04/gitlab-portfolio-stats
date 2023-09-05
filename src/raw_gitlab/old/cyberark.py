import requests
import os

# Mock list of safe IDs for demonstration. Replace these with your actual safe IDs.
SAFE_IDS = ["Safe1", "Safe2", "Safe3"]

BASE_URL = os.environ.get("CYBERARK_PVWA_URL")

def get_accounts_from_safe(safe_id: str, cert_file_path: str, key_file_path: str) -> list:
    url = f"{BASE_URL}/PasswordVault/WebAPI/Safes/{safe_id}/Accounts"  # Assuming this is the endpoint format
    cert = (cert_file_path, key_file_path)
    response = requests.get(url, cert=cert)
    response.raise_for_status()
    return response.json()

def get_account_activity(account_id: str, cert_file_path: str, key_file_path: str) -> dict:
    url = f"{BASE_URL}/PasswordVault/WebAPI/Accounts/{account_id}/Activities"
    cert = (cert_file_path, key_file_path)
    response = requests.get(url, cert=cert)
    response.raise_for_status()
    return response.json()

def fetch_all_activities_for_safes(cert_file_path: str, key_file_path: str) -> dict:
    all_activities = {}
    for safe_id in SAFE_IDS:
        accounts = get_accounts_from_safe(safe_id, cert_file_path, key_file_path)
        for account in accounts:
            account_id = account['ID']  # Assuming the account ID is stored under the key 'ID'
            all_activities[account_id] = get_account_activity(account_id, cert_file_path, key_file_path)
    return all_activities
