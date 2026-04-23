import getpass
from pathlib import Path

def _load_env() -> dict:
    env_path = Path(__file__).parent.parent / ".env"
    env = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env

def login() -> tuple[str, str]:
    """Returns (username, private_key). Reads from .env if populated, otherwise prompts."""
    env = _load_env()

    username = env.get("RS_USERNAME") or input("ResourceSpace username: ").strip()
    private_key = env.get("RS_API_KEY") or getpass.getpass("API key (from your RS user profile): ")

    if not username or not private_key:
        raise ValueError("Username and API key are required.")

    return username, private_key
