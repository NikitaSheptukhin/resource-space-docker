import hmac, hashlib, requests, os, getpass

# base_url = os.environ.get("resourcespace_api_url")
base_url = "http://10.172.18.178"

def get_credentials() -> tuple[str, str]:
    """Prompt the user for their ResourceSpace credentials via the console."""
    username = input("ResourceSpace username: ").strip()
    password = getpass.getpass("Password: ")
    return username, password


def login(username: str, password: str) -> str:
    """Authenticate with ResourceSpace and return a session key."""
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


def sign_request(session_key: str, query_string: str) -> str:
    """Generate the SHA-256 signature for an API call using the session key."""
    return hashlib.sha256((session_key + query_string).encode()).hexdigest()


if __name__ == "__main__":
    username, password = get_credentials()
    session_key = login(username, password)
