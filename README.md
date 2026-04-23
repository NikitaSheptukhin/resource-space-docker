# resourcespace/docker

The official Docker image for ResourceSpace. Full build instructions can be found on our [Knowledge Base](https://www.resourcespace.com/knowledge-base/systemadmin/install_docker).

# Starting ResourseSpace

* Start ResourceSpace with the following command: `source start.sh`
* ResourceSpace will start on port 8000
    - To change the port to another value update the 5 following files:
        - [start.sh](./start.sh) for RESOURCESPACE_HOST
        - [docker-compose.yaml](./docker-compose.yaml) under host ports for resourcespace
        - [config.php](./config.php) at baseurl
        - [000-default.conf](./000-default.conf) at \<VirtualHost\>
        - [entrypoint.sh](./entrypoint.sh) around line 38 for EFFECTIVE_BASEURL

# Installation notes

- Before building the Docker image, change the db.env file replacing the default "change-me" passwords to secure values.
- When setting up ResourceSpace ensure you enter "mariadb" as the MySQL server instead of "localhost" and leave the "MySQL binary path" empty.

# Default admin credentials

On first startup, the automated setup creates an admin user with:

- Username: `admin`
- Password: `Adminpass1!`

If setup falls back to admin bootstrap recovery, the admin password is set to:

- Password: `RSadminAdminpass1!`

For security, change the admin password immediately after first login.
