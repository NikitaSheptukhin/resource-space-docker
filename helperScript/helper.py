import hashlib
import requests

def _signed_get(base_url: str, path: str, username: str, private_key: str, params: dict):
    query = "&".join(f"{k}={v}" for k, v in params.items()) + f"&user={username}"
    sign = hashlib.sha256((private_key + query).encode()).hexdigest()
    resp = requests.get(f"{base_url}/{path}?{query}&sign={sign}", timeout=15)
    resp.raise_for_status()
    try:
        return resp.json()
    except Exception:
        return resp.text.strip()

def api_call(base_url: str, username: str, private_key: str, params: dict):
    return _signed_get(base_url, "api/", username, private_key, params)

def helper_call(base_url: str, username: str, private_key: str, params: dict):
    return _signed_get(base_url, "rs_helper/", username, private_key, params)