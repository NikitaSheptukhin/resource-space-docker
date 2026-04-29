"""
provisioner.py — High-level provisioning for a named collection with a
single scoped user group.

Usage
-----
    from provisioner import provision_collection_space

    result = provision_collection_space(
        base_url="http://10.172.18.178",
        username=username,
        private_key=private_key,
        name="Biology_Dept",
    )
    print(result)
    # Collection 'Biology_Dept' (id=42)
    #   group id : 7

Group semantics
---------------
{name}_members   Full CRUD (upload/edit/delete) on every resource inside the
                 collection; read + download on any resource system-wide.
                 Cannot modify the collection itself and cannot edit or delete
                 resources that live outside this collection.
"""

from __future__ import annotations

from dataclasses import dataclass

from rs_collections import create_collection, set_collection_public, set_collection_featured
from user_groups import (
    COLLECTION_MEMBER_PERMISSIONS,
    create_user_group,
    set_group_collection_access,
)


@dataclass
class ProvisionResult:
    collection_name: str
    collection_id: int
    group_id: int

    def __str__(self) -> str:  # pragma: no cover
        return (
            f"Collection '{self.collection_name}' (id={self.collection_id})\n"
            f"  group id : {self.group_id}"
        )


def provision_collection_space(
    base_url: str,
    username: str,
    private_key: str,
    name: str,
    public_collection: bool = False,
    featured_collection: bool = False,
) -> ProvisionResult:
    """
    Create a collection and one scoped user group for *name*.

    Steps
    -----
    1. Create collection  →  ``{name}``
    2. Optionally mark it public/private and/or featured.
    3. Create group       →  ``{name}_members``
       - permissions: r,s,c,e*,d,b,f*,j*,z
         (full CRUD inside collection; read/download everywhere)
       - collection access level 0 (full access to all resources in collection)

    Parameters
    ----------
    base_url:
        Root URL of the ResourceSpace instance, e.g. ``http://10.172.18.178``.
    username:
        Username of the authenticated API user.
    private_key:
        Private API key obtained via ``auth.login()``.
    name:
        Base name for the collection and group.  Avoid spaces; use underscores.
    public_collection:
        Whether to mark the collection as publicly visible (default False).
    featured_collection:
        Whether to mark the collection as featured on the RS homepage (default False).
        Requires the ``featured`` column to exist in the RS ``collection`` table.

    Returns
    -------
    ProvisionResult
        Dataclass with ``collection_id`` and ``group_id``.

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
    if featured_collection:
        set_collection_featured(base_url, username, private_key, collection_id)

    # ── 2. Single member group ───────────────────────────────────────────────
    group_name = f"{name}_members"
    group_id = create_user_group(
        base_url, username, private_key,
        name=group_name,
        permissions=COLLECTION_MEMBER_PERMISSIONS,
    )
    # access_level=0 → full CRUD on every resource in the collection
    set_group_collection_access(
        base_url, username, private_key,
        group_id=group_id,
        collection_id=collection_id,
        access_level=0,
    )

    return ProvisionResult(
        collection_name=name,
        collection_id=collection_id,
        group_id=group_id,
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

    remove_group_collection_access(
        base_url, username, private_key,
        group_id=result.group_id,
        collection_id=result.collection_id,
    )
