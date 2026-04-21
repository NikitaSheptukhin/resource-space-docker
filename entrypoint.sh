#!/bin/bash

# Start cron service
service cron start

# Ensure daily cron jobs are executable
chmod +x /etc/cron.daily/*

# Copy config with correct permissions
cp /tmp/config.php /var/www/html/include/config.php
chmod 775 /var/www/html/include/config.php
chown root:www-data /var/www/html/include/config.php

# Start Apache in the foreground (keeps the container alive)
apachectl -D FOREGROUND
