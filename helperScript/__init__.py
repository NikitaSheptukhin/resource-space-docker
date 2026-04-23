"""
resourcespace — collection provisioning utilities.
"""

from .provisioner import ProvisionResult, provision_collection_space, teardown_collection_space
from .rs_collections import create_collection, get_collection, set_collection_public
from .user_groups import (
    create_user_group,
    get_user_group,
    set_group_collection_access,
    remove_group_collection_access,
    add_user_to_group,
    ADMIN_FACULTY_PERMISSIONS,
    FACULTY_PERMISSIONS,
)
from .auth import login
from .helper import api_call

__all__ = [
    "provision_collection_space",
    "teardown_collection_space",
    "ProvisionResult",
    "create_collection",
    "get_collection",
    "set_collection_public",
    "create_user_group",
    "get_user_group",
    "set_group_collection_access",
    "remove_group_collection_access",
    "add_user_to_group",
    "ADMIN_FACULTY_PERMISSIONS",
    "FACULTY_PERMISSIONS",
    "login",
    "api_call"
]
