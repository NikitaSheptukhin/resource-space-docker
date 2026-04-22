"""
provisioner.py — High-level provisioning for a named collection with
admin_faculty and faculty user groups.

Usage
-----
    from resourcespace.provisioner import provision_collection_space

    result = provision_collection_space(
        base_url="http://10.172.18.178",
        session_key=session_key,
        api_user="admin",
        name="Biology_Dept",
    )
    print(result)
    # {
    #   "collection_id": 42,
    #   "admin_faculty_group_id": 7,
    #   "faculty_group_id": 8,
    # }

Group semantics
---------------
admin_faculty   Full CRUD on *all* resources in the collection (permissions: rsedcbz).
                Can search, view, edit, delete, create, bulk-operate, and is
                scoped to the collection via the 'z' flag.

faculty         CRUD only on resources *they upload* to the collection
                (permissions: rscz + upload-owner access level 1).
                Members can search/view all resources in the collection but
                may only edit/delete their own uploads.
"""

from __future__ import annotations

from dataclasses import dataclass

from rs_collections import create_collection, set_collection_public
from user_groups import (
    ADMIN_FACULTY_PERMISSIONS,
    FACULTY_PERMISSIONS,
    create_user_group,
    set_group_collection_access,
)


@dataclass
class ProvisionResult:
    collection_name: str
    collection_id: int
    admin_faculty_group_id: int
    faculty_group_id: int

    def __str__(self) -> str:  # pragma: no cover
        return (
            f"Collection '{self.collection_name}' (id={self.collection_id})\n"
            f"  admin_faculty group id : {self.admin_faculty_group_id}\n"
            f"  faculty group id       : {self.faculty_group_id}"
        )


def provision_collection_space(
    base_url: str,
    username: str,
    private_key: str,
    name: str,
    public_collection: bool = False,
) -> ProvisionResult:
    """
    Create a collection and two scoped user groups for *name*.

    Steps
    -----
    1. Create collection  →  ``{name}``
    2. Optionally mark it public/private.
    3. Create group       →  ``{name}_admin_faculty``
       - permissions: rsedcbz (full CRUD + collection scope)
       - collection access level 0 (full access to all resources)
    4. Create group       →  ``{name}_faculty``
       - permissions: rscz (search, view, create + collection scope)
       - collection access level 1 (can only edit/delete own uploads)

    Parameters
    ----------
    base_url:
        Root URL of the ResourceSpace instance, e.g. ``http://10.172.18.178``.
    username:
        Username of the authenticated API user.
    private_key:
        Private API key obtained via ``auth.login()``.
    name:
        Base name for the collection and groups.  Avoid spaces; use underscores.
    public_collection:
        Whether to mark the collection as publicly visible (default False).

    Returns
    -------
    ProvisionResult
        Dataclass with ``collection_id``, ``admin_faculty_group_id``,
        ``faculty_group_id``.

    Raises
    ------
    RuntimeError
        If any API step returns a non-positive ID.
    requests.HTTPError
        On network-level failures.
    """
    # ── 1. Collection ────────────────────────────────────────────────────────
    collection_id = create_collection(base_url, username, private_key, name)
    set_collection_public(base_url, username, private_key, collection_id, public_collection)

    # ── 2. admin_faculty group ───────────────────────────────────────────────
    admin_group_name = f"{name}_admin_faculty"
    admin_group_id = create_user_group(
        base_url, username, private_key,
        name=admin_group_name,
        permissions=ADMIN_FACULTY_PERMISSIONS,
    )
    # access_level=0 → full CRUD on every resource in the collection
    set_group_collection_access(
        base_url, username, private_key,
        group_id=admin_group_id,
        collection_id=collection_id,
        access_level=0,
    )

    # ── 3. faculty group ─────────────────────────────────────────────────────
    faculty_group_name = f"{name}_faculty"
    faculty_group_id = create_user_group(
        base_url, username, private_key,
        name=faculty_group_name,
        permissions=FACULTY_PERMISSIONS,
    )
    # access_level=1 → members can only edit/delete their own uploads
    set_group_collection_access(
        base_url, username, private_key,
        group_id=faculty_group_id,
        collection_id=collection_id,
        access_level=1,
    )

    return ProvisionResult(
        collection_name=name,
        collection_id=collection_id,
        admin_faculty_group_id=admin_group_id,
        faculty_group_id=faculty_group_id,
    )


def teardown_collection_space(
    base_url: str,
    username: str,
    private_key: str,
    result: ProvisionResult,
) -> None:
    """
    Convenience helper to undo a ``provision_collection_space`` call during
    testing.  Not a substitute for a proper archiving workflow in production.
    """
    from user_groups import remove_group_collection_access

    for gid in (result.admin_faculty_group_id, result.faculty_group_id):
        remove_group_collection_access(
            base_url, username, private_key,
            group_id=gid,
            collection_id=result.collection_id,
        )
