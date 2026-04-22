from provisioner import provision_collection_space, teardown_collection_space
from auth import login

base_url = "http://10.172.18.178"
api_scramble_key = "c0c7f6563b9dc69b6bcdccf5c8e83dca7e95fd62a34e3e8ad5c17e71a2ec2ede"

if __name__ == "__main__":
    username, private_key = login(base_url, api_scramble_key)
    print(username)
    print(private_key)

    # ── Provision a named collection space ───────────────────────────────────
    result = provision_collection_space(
        base_url=base_url,
        username=username,
        private_key=private_key,
        name="Biology_Dept",        # base name — no spaces recommended
        public_collection=False,
    )

    print(result)
    # Collection 'Biology_Dept' (id=42)
    #   admin_faculty group id : 7
    #   faculty group id       : 8

    # ── Optionally tear down (useful in tests / dev) ─────────────────────────
    # teardown_collection_space(base_url, username, private_key, result)
