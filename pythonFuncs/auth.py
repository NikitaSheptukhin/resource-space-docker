import requests, getpass

def get_credentials() -> tuple[str, str]:
    """Prompt the user for their ResourceSpace credentials via the console."""
    username = input("ResourceSpace username: ").strip()
    password = getpass.getpass("Password: ")
    return username, password


def login(base_url: str) -> str:
    """Authenticate with ResourceSpace and return a session key."""
    username, password = get_credentials()
    response = requests.get(f"{base_url}/api/", params={
        "function": "login",
        "username": username,
        "password": password,
    })
    response.raise_for_status()

    session_key = response.text.strip()
    if session_key.lower() == "false" or not session_key:
        raise ValueError("Login failed: invalid username or password.")
    return session_key




