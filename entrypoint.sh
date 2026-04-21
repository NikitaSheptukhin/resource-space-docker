#!/bin/bash

# Start cron service
service cron start

# Ensure daily cron jobs are executable
chmod +x /etc/cron.daily/*

# Start Apache in the foreground (keeps the container alive)
apachectl -D FOREGROUND

curl -s -X POST http://localhost/pages/setup.php \
   --data-urlencode "submit=Begin installation!" \
   --data-urlencode "mysql_server=mariadb" \
   --data-urlencode "mysql_username=resourcespace_rw" \
   --data-urlencode "mysql_password=rs_test_password" \
   --data-urlencode "mysql_db=resourcespace" \
   --data-urlencode "baseurl=http://resourcespace/" \
   --data-urlencode "admin_fullname=Admin User" \
   --data-urlencode "admin_username=admin" \
   --data-urlencode "admin_password=Adminpass1!" \
   --data-urlencode "admin_email=test@test.test" \
   --data-urlencode "email_from=test@test.test"

# Update baseurl in config.php with RESOURCESPACE_HOST environment variable
sed -i "s|\$baseurl = '.*'|\$baseurl = '$RESOURCESPACE_HOST'|" /var/www/html/config.php
