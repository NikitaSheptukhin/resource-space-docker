# resourcespace/docker

The official Docker image for ResourceSpace. Full build instructions can be found on our [Knowledge Base](https://www.resourcespace.com/knowledge-base/systemadmin/install_docker).

# Starting ResourseSpace

* ResourceSpace will start on port 8000
    - ## **Update [config.php](./config.php) with your IP and port for baseurl**
    - To change the port to another value update the 5 following files:
        - [start.sh](./start.sh) for RESOURCESPACE_HOST
        - [docker-compose.yaml](./docker-compose.yaml) under host ports for resourcespace
        - [config.php](./config.php) at baseurl
        - [000-default.conf](./000-default.conf) at \<VirtualHost\>
        - [entrypoint.sh](./entrypoint.sh) around line 38 for EFFECTIVE_BASEURL
* Start ResourceSpace with the following command: `source start.sh`

# Installation notes

- Before building the Docker image, change the db.env file replacing the default "change-me" passwords to secure values.
- When setting up ResourceSpace ensure you enter "mariadb" as the MySQL server instead of "localhost" and leave the "MySQL binary path" empty.

# Python script
There is a script incuded in the repo which allow for quick and seamless creation of a resource collection and associated admin and normal faculty user groups.

## Instructions
- copy the example.env file in root and rename it to .env
- replace all the temp values to actual values
    - RS_BASE_URL: Url of the ResourceSpace machine
    - RS_USERNAME: Your ResourceSpace Username
    - RS_API_KEY: Your private api key found in the Admin Panel -> Users -> Edit (your user) -> Private API Key -> Show hidden property
- run `python helperScript/main.py`
- input collection name

# Default admin credentials

On first startup, the automated setup creates an admin user with:

- Username: `admin`
- Password: `Adminpass1!`

If setup falls back to admin bootstrap recovery, the admin password is set to:

- Password: `RSadminAdminpass1!`

For security, change the admin password immediately after first login.
