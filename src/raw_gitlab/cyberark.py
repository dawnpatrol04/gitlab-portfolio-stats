import os

BASE_URL = os.environ.get("CYBERARK_PVWA_URL")

if not BASE_URL:
    raise ValueError("The environment variable 'CYBERARK_PVWA_URL' is not set.")

def list_all_accounts(cert_file_path: str, key_file_path: str) -> list:
    url = f"{BASE_URL}/PasswordVault/WebServices/PIMServices.svc/Accounts"
    cert = (cert_file_path, key_file_path)
    response = requests.get(url, cert=cert)
    response.raise_for_status()
    return response.json()

def get_account_activity(account_id: str, cert_file_path: str, key_file_path: str) -> dict:
    url = f"{BASE_URL}/PasswordVault/WebServices/PIMServices.svc/Accounts/{account_id}/Activities"
    cert = (cert_file_path, key_file_path)
    response = requests.get(url, cert=cert)
    response.raise_for_status()
    return response.json()
