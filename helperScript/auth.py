import requests, getpass, hashlib

def get_credentials() -> tuple[str, str]:
    username = input("ResourceSpace username: ").strip()
    password = getpass.getpass("Password: ")
    return username, password

def login(base_url: str, api_scramble_key: str) -> tuple[str, str]:
    """Returns (username, private_key). Verifies credentials then derives the API key."""
    username, password = get_credentials()

    # Login bypasses signature checking server-side. param2 must be plain text —
    # RS passes it directly to rs_password_verify().
    query = f"function=login&param1={username}&param2={password}"
    response = requests.get(f"{base_url}/api/?{query}&user={username}", timeout=15)
    response.raise_for_status()

    result = response.text.strip().strip('"')
    if not result or result.lower() == "false":
        raise ValueError("Login failed: invalid credentials.")

    # Derives the API key the same way get_api_key() does in RS: sha256(username + api_scramble_key).
    private_key = hashlib.sha256((username + api_scramble_key).encode()).hexdigest()
    return username, private_key