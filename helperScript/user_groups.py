"""
user_groups.py — ResourceSpace user-group management.

ResourceSpace permission flags (bitmask used in `permissions` column):
    r   = search / view resources
    s   = download original
    e   = edit resource metadata
    d   = delete resources
    c   = create (upload) resources
    h   = access restricted resources
    t   = create resource types
    u   = manage users
    g   = manage user groups
    a   = system administration
    b   = bulk operations
    z   = resource-level access (required for collection-restricted groups)

For collection-scoped groups the key flag is `z` (restrict by collection),
combined with the CRUD subset you want to grant.
"""

from helper import api_call, helper_call



# ---------------------------------------------------------------------------
# Permission-string helpers
# ---------------------------------------------------------------------------

# Full CRUD (upload/edit/delete) on any resource inside their collection.
# r,s grant read/download on ALL resources system-wide (outside the collection);
# c,e*,d,b are scoped to the collection by `z` — members cannot modify the
# collection itself (no a/u/g flags) nor edit resources outside it.
COLLECTION_MEMBER_PERMISSIONS = "r,s,c,e-2,e-1,e0,e1,e3,d,b,f*,j*,z"

def create_user_group(
    base_url: str,
    username: str,
    private_key: str,
    name: str,
    permissions: str,
    parent: int = 0,
) -> int:
    """
    Create a user group with the given permission string.
    Returns the new group's numeric ID.
    """
    result = helper_call(base_url, username, private_key, {
        "function": "create_group",
        "param1": name,
        "param2": permissions,
        "param3": parent,
    })
    group_id = int(result)
    if group_id <= 0:
        raise RuntimeError(f"Failed to create group '{name}': API returned {result}")
    return group_id


def get_user_group(
    base_url: str, username: str, private_key: str, group_id: int
) -> dict:
    """Return the group record as a dict."""
    return api_call(base_url, username, private_key, {
        "function": "get_usergroup",
        "param1": group_id,
    })


def set_group_collection_access(
    base_url: str,
    username: str,
    private_key: str,
    group_id: int,
    collection_id: int,
    access_level: int = 0,
) -> None:
    """
    Grant a user group access to a specific collection.

    access_level:
        0 = full access to all resources in the collection
        1 = access only to resources they uploaded (upload-owner restriction)
    """
    helper_call(base_url, username, private_key, {
        "function": "add_group_collection_access",
        "param1": group_id,
        "param2": collection_id,
    })


def remove_group_collection_access(
    base_url: str,
    username: str,
    private_key: str,
    group_id: int,
    collection_id: int,
) -> None:
    """Remove a user group's access to a specific collection."""
    helper_call(base_url, username, private_key, {
        "function": "delete_group_collection_access",
        "param1": group_id,
        "param2": collection_id,
    })


def add_user_to_group(
    base_url: str, username: str, private_key: str,
    target_username: str, group_id: int
) -> None:
    """Assign an existing user to a group."""
    helper_call(base_url, username, private_key, {
        "function": "update_user_group",
        "param1": target_username,
        "param2": group_id,
    })
