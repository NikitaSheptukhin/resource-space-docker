#!/bin/bash
set -e

# Container startup flow:
# 1) start required services,
# 2) resolve a usable base URL,
# 3) ensure setup has produced at least one user,
# 4) keep Apache in the foreground as PID 1.

# Start cron service
service cron start

# Ensure daily cron jobs are executable
chmod +x /etc/cron.daily/*

# Initialize database and admin user (must happen before setup attempts)
bash /var/www/html/init.sh

# Ensure base URL is set correctly for browser-facing origin.
RESOURCESPACE_HOST="${RESOURCESPACE_HOST:-}"
CONFIG_PATH="/var/www/html/include/config.php"
SETUP_MARKER="/var/www/html/filestore/.setup_complete"
EFFECTIVE_BASEURL=""

# Prefer an explicit host provided via environment.
# Otherwise, reuse the configured value from include/config.php.
if [[ -f "$CONFIG_PATH" ]]; then
   EFFECTIVE_BASEURL="$(sed -n "s/^\$baseurl = '\(.*\)';/\1/p" "$CONFIG_PATH" | head -n 1)"

   if [[ -n "$RESOURCESPACE_HOST" ]]; then
      temp_config="$(mktemp)"
      sed "s|\$baseurl = '.*'|\$baseurl = '$RESOURCESPACE_HOST'|" "$CONFIG_PATH" > "$temp_config"
      cat "$temp_config" > "$CONFIG_PATH"
      rm -f "$temp_config"
      EFFECTIVE_BASEURL="$RESOURCESPACE_HOST"
   fi
fi

# Last-resort default for local access when no base URL is discoverable.
if [[ -z "$EFFECTIVE_BASEURL" ]]; then
   EFFECTIVE_BASEURL="http://127.0.0.1:8000"
fi

setup_config_backup=""

# Return the number of rows in the user table.
# Emits an empty string if DB/table is not ready yet.
get_user_count()
{
   php -r '
      $host = "mariadb";
      $user = getenv("MYSQL_USER") ?: "resourcespace_rw";
      $pass = getenv("MYSQL_PASSWORD") ?: "rs_test_password";
      $db   = getenv("MYSQL_DATABASE") ?: "resourcespace";
      mysqli_report(MYSQLI_REPORT_OFF);
      $conn = @new mysqli($host, $user, $pass, $db, 3306);
      if($conn->connect_errno)
          {
          echo "";
          exit(0);
          }
      $result = $conn->query("SELECT COUNT(*) AS c FROM user");
      if($result === false)
          {
          echo "";
          exit(0);
          }
      $row = $result->fetch_assoc();
      echo isset($row["c"]) ? (string)$row["c"] : "";
   '
}

# Ensure at least one admin account exists when setup partially fails.
# Returns resulting user count or empty string on failure.
   ensure_admin_user_exists()
   {
      php -r '
        $host = "mariadb";
        $user = getenv("MYSQL_USER") ?: "resourcespace_rw";
        $pass = getenv("MYSQL_PASSWORD") ?: "rs_test_password";
        $db   = getenv("MYSQL_DATABASE") ?: "resourcespace";

        mysqli_report(MYSQLI_REPORT_OFF);
        $conn = @new mysqli($host, $user, $pass, $db, 3306);
        if($conn->connect_errno)
           {
           echo "";
           exit(0);
           }

        $table_check = $conn->query("SHOW TABLES LIKE \"user\"");
        if($table_check === false || $table_check->num_rows === 0)
           {
           echo "";
           exit(0);
           }

        $count_result = $conn->query("SELECT COUNT(*) AS c FROM user");
        if($count_result === false)
           {
           echo "";
           exit(0);
           }
        $count_row = $count_result->fetch_assoc();
        $existing = isset($count_row["c"]) ? (int)$count_row["c"] : 0;
        if($existing > 0)
           {
           echo (string)$existing;
           exit(0);
           }

        require_once "/var/www/html/include/db.php";
        require_once "/var/www/html/include/general_functions.php";
        require_once "/var/www/html/include/login_functions.php";
        require_once "/var/www/html/include/user_functions.php";

        $admin_ref = ps_value("SELECT ref value FROM user WHERE username = ?", ["s", "admin"], 0);
        if($admin_ref <= 0)
           {
           $admin_ref = new_user("admin", 1);
           }

        if($admin_ref > 0)
           {
           $hash = rs_password_hash("RSadminAdminpass1!");
           ps_query(
              "UPDATE user SET password = ?, fullname = ?, email = ?, usergroup = 1, approved = 1 WHERE ref = ?",
              ["s", $hash, "s", "Admin User", "s", "test@test.test", "i", (int)$admin_ref]
           );
           $final_count = ps_value("SELECT COUNT(*) value FROM user", [], 0);
           echo (string)$final_count;
           exit(0);
           }

        echo "";
      '
   }

# Start Apache in the background so setup can use HTTP endpoints.
apachectl -D FOREGROUND &
apache_pid=$!

cleanup()
{
   if [[ -n "${apache_pid:-}" ]] && kill -0 "$apache_pid" 2>/dev/null; then
      kill "$apache_pid"
   fi
}
trap cleanup EXIT

# Wait until Apache is responding before running setup.
apache_ready=false
for _ in {1..30}; do
   if curl -fs "http://127.0.0.1/pages/setup.php" >/dev/null 2>&1; then
      apache_ready=true
      break
   fi
   sleep 1
done

# Run setup when first starting or whenever the DB has no users.
# Marker avoids rerunning setup on healthy restarts.
user_count="$(get_user_count)"
needs_setup=false
if [[ ! -f "$SETUP_MARKER" ]]; then
   needs_setup=true
elif [[ -z "$user_count" || "$user_count" == "0" ]]; then
   needs_setup=true
fi

if [[ "$apache_ready" == "true" && "$needs_setup" == "true" ]]; then
   # setup.php refuses to run when include/config.php exists with content.
   # If DB is empty, truncate config temporarily so setup can bootstrap tables.
   if [[ -f "$CONFIG_PATH" && -s "$CONFIG_PATH" ]]; then
      setup_config_backup="$(mktemp)"
      cat "$CONFIG_PATH" > "$setup_config_backup"
      : > "$CONFIG_PATH"
   fi

   # Primary path: drive the web installer non-interactively.
   setup_ok=true
   if ! curl -fsS -X POST "http://127.0.0.1/pages/setup.php" \
      --data-urlencode "submit=Begin installation!" \
      --data-urlencode "mysql_server=mariadb" \
      --data-urlencode "mysql_username=${MYSQL_USER:-resourcespace_rw}" \
      --data-urlencode "mysql_password=${MYSQL_PASSWORD:-rs_test_password}" \
      --data-urlencode "mysql_db=${MYSQL_DATABASE:-resourcespace}" \
      --data-urlencode "baseurl=${EFFECTIVE_BASEURL}" \
      --data-urlencode "admin_fullname=Admin User" \
      --data-urlencode "admin_username=admin" \
      --data-urlencode "admin_password=Adminpass1!" \
      --data-urlencode "admin_email=test@test.test" \
      --data-urlencode "email_from=test@test.test" >/dev/null; then
      setup_ok=false
   fi

   # Success criteria is both installer response and a non-empty user table.
   user_count_after_setup="$(get_user_count)"
   if [[ "$setup_ok" == "true" && -n "$user_count_after_setup" && "$user_count_after_setup" != "0" ]]; then
      touch "$SETUP_MARKER"
      rm -f "$setup_config_backup"
      setup_config_backup=""
   else
      # Fallback path: force-create/fix admin user if setup response was inconclusive.
      admin_bootstrap_count="$(ensure_admin_user_exists)"
      if [[ -n "$admin_bootstrap_count" && "$admin_bootstrap_count" != "0" ]]; then
         touch "$SETUP_MARKER"
         rm -f "$setup_config_backup"
         setup_config_backup=""
      elif [[ -n "$setup_config_backup" && -f "$setup_config_backup" ]]; then
         # Restore prior config when setup/bootstrap did not complete safely.
         cat "$setup_config_backup" > "$CONFIG_PATH"
         rm -f "$setup_config_backup"
         setup_config_backup=""
         echo "Setup did not complete successfully; restored previous config." >&2
      fi
   fi
fi

# Keep Apache as the main container process.
wait "$apache_pid"
