#!/bin/bash
set -e

# Container startup flow:
# 1) start required services,
# 2) apply base URL override when provided,
# 3) run deterministic initialization,
# 4) keep Apache in the foreground as PID 1.

# Start cron service
service cron start

# Ensure daily cron jobs are executable
chmod +x /etc/cron.daily/*

# Ensure base URL is set correctly for browser-facing origin.
RESOURCESPACE_HOST="${RESOURCESPACE_HOST:-}"
CONFIG_PATH="/var/www/html/include/config.php"
if [[ -f "$CONFIG_PATH" && -n "$RESOURCESPACE_HOST" ]]; then
   temp_config="$(mktemp)"
   sed "s|\$baseurl = '.*'|\$baseurl = '$RESOURCESPACE_HOST'|" "$CONFIG_PATH" > "$temp_config"
   cat "$temp_config" > "$CONFIG_PATH"
   rm -f "$temp_config"
fi

# Initialize database and admin user.
bash /var/www/html/init.sh

# Keep Apache as the main container process.
exec apachectl -D FOREGROUND
