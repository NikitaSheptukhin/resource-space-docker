import re
from auth import login, _load_env
from provisioner import provision_collection_space, teardown_collection_space

if __name__ == "__main__":
    base_url = _load_env().get("RS_BASE_URL", "http://10.172.18.178")
    username, private_key = login()

    # ── Provision a named collection space ───────────────────────────────────
    while True:
        name = input("Enter collection name (no spaces, letters/digits/underscores/hyphens only): ").strip()
        if name and re.match(r'^[\w-]+$', name):
            break
        print("Invalid name. Use only letters, digits, underscores, or hyphens — no spaces.")

    result = provision_collection_space(
        base_url=base_url,
        username=username,
        private_key=private_key,
        name=name,
        public_collection=False,
    )

    print(result)
    # Collection 'Biology_Dept' (id=42)
    #   admin_faculty group id : 7
    #   faculty group id       : 8

    # ── Optionally tear down (useful in tests / dev) ─────────────────────────
    # teardown_collection_space(base_url, username, private_key, result)
