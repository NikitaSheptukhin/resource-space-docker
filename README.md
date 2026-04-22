# resourcespace/docker

The official Docker image for ResourceSpace. Full build instructions can be found on our [Knowledge Base](https://www.resourcespace.com/knowledge-base/systemadmin/install_docker).

# Starting ResourseSpace

Start ResourceSpace with the following command: `source start.sh`

# Installation notes

- Before building the Docker image, change the db.env file replacing the default "change-me" passwords to secure values.
- When setting up ResourceSpace ensure you enter "mariadb" as the MySQL server instead of "localhost" and leave the "MySQL binary path" empty.
