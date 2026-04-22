import hmac, hashlib, requests, os, getpass
from pythonFuncs import auth 

# base_url = os.environ.get("resourcespace_api_url")
base_url = "http://10.172.18.178"

def sign_request(session_key: str, query_string: str) -> str:
    """Generate the SHA-256 signature for an API call using the session key."""
    return hashlib.sha256((session_key + query_string).encode()).hexdigest()


if __name__ == "__main__":
    session_key = auth.login(base_url)
    # print(session_key)