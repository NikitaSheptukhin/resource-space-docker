# Using an Existing MySQL Server for ResourceSpace

## Connection Configuration

All database connection settings live in `config/config.php`:

```php
$mysql_server   = "192.168.1.100";   // IP or hostname of your existing server
$mysql_username = "resourcespace";
$mysql_password = "yourpassword";
$mysql_database = "resourcespace";
$mysql_port     = 3306;              // default, change if needed
$mysql_ssl      = false;             // set true if using SSL connections
```

---

## MySQL Server Requirements

**Version compatibility** — ResourceSpace requires:
- MySQL **5.7+** or **8.0+** (recommended)
- MariaDB **10.3+** is also supported

**Required privileges** for the ResourceSpace database user:

```sql
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, 
      ALTER, CREATE TEMPORARY TABLES, LOCK TABLES 
ON resourcespace.* TO 'resourcespace'@'%' IDENTIFIED BY 'yourpassword';

FLUSH PRIVILEGES;
```

> It needs `CREATE`, `DROP`, and `ALTER` not just for initial setup, but because ResourceSpace applies **database schema migrations** automatically on upgrade — so the user needs DDL privileges permanently, not just at install time.

---

## Network & Access Considerations

**Allow remote connections** — by default MySQL often binds only to `127.0.0.1`. On your existing server check:

```ini
# /etc/mysql/mysql.conf.d/mysqld.cnf
bind-address = 0.0.0.0   # or the specific IP ResourceSpace will connect from
```

**Firewall** — ensure port `3306` (or your custom port) is open between the ResourceSpace web server and the MySQL host.

**Host-based access** — the MySQL user must be created to allow connections from the ResourceSpace server's IP, not just `localhost`:

```sql
CREATE USER 'resourcespace'@'192.168.1.50' IDENTIFIED BY 'password';
-- or for any host (less secure):
CREATE USER 'resourcespace'@'%' IDENTIFIED BY 'password';
```

---

## Database & Character Set Setup

Create the database with the correct character set **before** running the ResourceSpace installer:

```sql
CREATE DATABASE resourcespace
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

Using `utf8mb4` is important for full Unicode support (emojis, non-Latin metadata, etc.). If the database is created with the wrong collation, you may get garbled metadata or failed inserts for certain characters.

---

## MySQL 8.0 Specific Gotchas

If your existing server runs **MySQL 8.0**, watch out for:

**Authentication plugin change** — MySQL 8 defaults to `caching_sha2_password`, but some PHP MySQL drivers expect `mysql_native_password`. If you get connection errors:

```sql
ALTER USER 'resourcespace'@'%' 
IDENTIFIED WITH mysql_native_password BY 'yourpassword';
```

**SQL mode strictness** — MySQL 8 has stricter SQL modes by default. ResourceSpace generally handles this, but if you see query errors check:

```sql
SELECT @@sql_mode;
```

You may need to remove `ONLY_FULL_GROUP_BY` or `STRICT_TRANS_TABLES` from the mode if legacy queries fail:

```ini
# In mysqld.cnf
sql_mode = "NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION"
```

---

## Shared Server Considerations

Since this is an **existing** MySQL server likely hosting other databases:

- **Isolate the user** — give the ResourceSpace user access *only* to the ResourceSpace database, not global privileges
- **Resource contention** — ResourceSpace can be query-intensive during indexing and batch processing; monitor for lock contention or slow query impact on other databases
- **Backup coordination** — ResourceSpace's database and filestore need to be backed up together to remain consistent; factor this into your existing backup schedule
- **Max connections** — ResourceSpace opens a connection per request; if your server has a low `max_connections` limit set, concurrent users may hit connection errors. Check:

```sql
SHOW VARIABLES LIKE 'max_connections';
```

---

## Installation

When you run the ResourceSpace web installer (`install/index.php`), it will:
1. Test the connection with your provided credentials
2. Create all tables and initial schema automatically
3. Insert default data (resource types, field definitions, system config)

The database just needs to **exist and be empty** — the installer handles the rest. If you're migrating an existing ResourceSpace instance rather than doing a fresh install, you'd restore a `mysqldump` instead.
