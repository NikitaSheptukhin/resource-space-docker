"""
rs_collections.py — ResourceSpace collection management.
"""

from helper import api_call, helper_call


# ---------------------------------------------------------------------------
# Collections
# ---------------------------------------------------------------------------

def create_collection(base_url: str, username: str, private_key: str, name: str) -> int:
    """Create a new collection and return its numeric ID."""
    result = api_call(base_url, username, private_key, {
        "function": "create_collection",
        "param1": name,
    })
    collection_id = int(result)
    if collection_id <= 0:
        raise RuntimeError(f"Failed to create collection '{name}': API returned {result}")
    return collection_id


def get_collection(base_url: str, username: str, private_key: str, collection_id: int) -> dict:
    """Fetch metadata for an existing collection."""
    return api_call(base_url, username, private_key, {
        "function": "get_collection",
        "param1": collection_id,
    })


def set_collection_public(
    base_url: str, username: str, private_key: str,
    collection_id: int, public: bool = False
) -> None:
    """Toggle the public flag on a collection (0 = private, 1 = public)."""
    helper_call(base_url, username, private_key, {
        "function": "set_collection_public",
        "param1": collection_id,
        "param2": int(public),
    })


def set_collection_featured(
    base_url: str, username: str, private_key: str,
    collection_id: int, featured: bool = True
) -> None:
    """Mark a collection as featured so it appears on the RS homepage."""
    helper_call(base_url, username, private_key, {
        "function": "set_collection_featured",
        "param1": collection_id,
        "param2": int(featured),
    })
