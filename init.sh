#!/bin/bash
# ResourceSpace initialization script - ensures database is ready and admin user exists

set -e

DB_HOST="mariadb"
DB_USER="${MYSQL_USER:-resourcespace_rw}"
DB_PASS="${MYSQL_PASSWORD:-rs_test_password}"
DB_NAME="${MYSQL_DATABASE:-resourcespace}"

echo "Waiting for database..."
for i in {1..60}; do
    if php -r "
        \$conn = @new mysqli('$DB_HOST', '$DB_USER', '$DB_PASS', '$DB_NAME', 3306);
        if (\$conn->connect_errno) {
            exit(1);
        }
        exit(0);
    " 2>/dev/null; then
        echo "Database ready"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "ERROR: Database connection timeout after 60 seconds"
        exit 1
    fi
    echo "Attempt $i/60..."
    sleep 1
done

# Initialize database tables and create admin user if needed
echo "Initializing ResourceSpace..."

php << 'EOF'
<?php
// Suppress output during boot
ob_start();
require_once '/var/www/html/include/boot.php';
require_once '/var/www/html/include/config.php';

// Initialize database structures
check_db_structs();
ob_end_clean();

// Now check and create admin user
$mysqli = new mysqli(
    getenv('MYSQL_HOST') ?: 'mariadb',
    getenv('MYSQL_USER') ?: 'resourcespace_rw',
    getenv('MYSQL_PASSWORD') ?: 'rs_test_password',
    getenv('MYSQL_DATABASE') ?: 'resourcespace'
);

if ($mysqli->connect_error) {
    die("Database error: " . $mysqli->connect_error);
}

// Check if admin user exists
$result = $mysqli->query("SELECT ref FROM user WHERE username='admin' LIMIT 1");
if ($result && $result->num_rows > 0) {
    echo "Admin user already exists\n";
    exit(0);
}

// Create admin user with correct password hashing
// ResourceSpace's rs_password_verify expects: RS{username}{password} format
$username = "admin";
$password = "Adminpass1!";
$fullname = "Admin User";
$email = "test@test.test";
$usergroup = 3;
$approved = 1;
$login_tries = 0;
$accepted_terms = 0;

// Use the same format as rs_password_verify expects
$scramble_key = $GLOBALS['scramble_key'] ?? "7f99d8e25ad1e65f3b21a7a864b83570093ce7bafdc8b343fa62c789c9610eb6";
$RS_madeup_pass = "RS" . $username . $password;  // This is what rs_password_verify expects
$hmac = hash_hmac('sha256', $RS_madeup_pass, $scramble_key);
$hash = password_hash($hmac, PASSWORD_DEFAULT);

$stmt = $mysqli->prepare(
    "INSERT INTO user (username, password, fullname, email, usergroup, approved, login_tries, accepted_terms) 
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
);

$stmt->bind_param('ssssiiii', $username, $hash, $fullname, $email, $usergroup, $approved, $login_tries, $accepted_terms);

if ($stmt->execute()) {
    echo "Admin user created successfully\n";
} else {
    die("Error creating admin user: " . $stmt->error);
}

$mysqli->close();
?>
EOF

# Mark setup complete
mkdir -p /var/www/html/filestore
touch /var/www/html/filestore/.setup_complete

echo "Initialization complete"

