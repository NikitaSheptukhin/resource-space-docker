# ResourceSpace Bare Metal Setup Guide
### Ubuntu 22.04 LTS — No Docker

---

## Overview

ResourceSpace is an open-source Digital Asset Management (DAM) system built on PHP/MySQL. This guide covers a full production-grade installation directly on a Linux server.

**Stack:**
- Ubuntu 22.04 LTS
- Apache 2.4
- PHP 8.1
- MySQL 8.0
- ImageMagick, FFmpeg, Ghostscript (media processing)

---

## 1. System Preparation

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget unzip git software-properties-common
```

Set your hostname:

```bash
sudo hostnamectl set-hostname resourcespace.yourdomain.com
```

---

## 2. Install Apache

```bash
sudo apt install -y apache2
sudo systemctl enable apache2
sudo systemctl start apache2
```

Enable required modules:

```bash
sudo a2enmod rewrite headers expires
sudo systemctl restart apache2
```

---

## 3. Install PHP 8.1

```bash
sudo add-apt-repository ppa:ondrej/php -y
sudo apt update
sudo apt install -y php8.1 php8.1-cli php8.1-common php8.1-mysql \
  php8.1-curl php8.1-gd php8.1-mbstring php8.1-xml php8.1-zip \
  php8.1-ldap php8.1-intl php8.1-bcmath php8.1-soap \
  libapache2-mod-php8.1
```

Verify:

```bash
php -v
```

### Tune PHP Settings

Edit `/etc/php/8.1/apache2/php.ini`:

```ini
upload_max_filesize = 500M
post_max_size = 500M
memory_limit = 512M
max_execution_time = 300
max_input_time = 300
```

---

## 4. Install MySQL 8.0

```bash
sudo apt install -y mysql-server
sudo systemctl enable mysql
sudo systemctl start mysql
```

Secure the installation:

```bash
sudo mysql_secure_installation
```

Create the ResourceSpace database and user:

```sql
sudo mysql -u root -p

CREATE DATABASE resourcespace CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'rsuser'@'localhost' IDENTIFIED BY 'StrongPassword123!';
GRANT ALL PRIVILEGES ON resourcespace.* TO 'rsuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## 5. Install Media Processing Tools

ResourceSpace relies on these tools to generate previews and transcode files.

```bash
# ImageMagick — image processing & thumbnails
sudo apt install -y imagemagick

# FFmpeg — video transcoding
sudo apt install -y ffmpeg

# Ghostscript — PDF/PostScript preview generation
sudo apt install -y ghostscript

# Exiftool — metadata extraction
sudo apt install -y libimage-exiftool-perl

# Antiword — legacy .doc text extraction (optional)
sudo apt install -y antiword

# Pdftotext / pdfinfo — PDF text indexing
sudo apt install -y poppler-utils
```

### Fix ImageMagick PDF Policy

By default, ImageMagick blocks PDF processing. Edit `/etc/ImageMagick-6/policy.xml`:

Find this line:

```xml
<policy domain="coder" rights="none" pattern="PDF" />
```

Change to:

```xml
<policy domain="coder" rights="read|write" pattern="PDF" />
```

---

## 6. Download ResourceSpace

```bash
cd /var/www/html
```

Download the latest release tarball directly

```bash
sudo wget https://www.resourcespace.com/downloads/ResourceSpace_Latest.tar.gz -O resourcespace.tar.gz
```

Verify it's actually a gzip file before extracting

```bash
file resourcespace.tar.gz
```

Extract

```bash
sudo mkdir resourcespace
sudo tar -xzf resourcespace.tar.gz -C resourcespace
sudo rm resourcespace.tar.gz
```

> **Tip:** Check https://www.resourcespace.com/knowledge-base/resourcespace/install for the latest download link.

Set correct ownership:

```bash
sudo chown -R www-data:www-data /var/www/html/resourcespace
sudo chmod -R 755 /var/www/html/resourcespace
sudo chmod -R 775 /var/www/html/resourcespace/filestore
```

---

## 7. Configure Apache Virtual Host

Create `/etc/apache2/sites-available/resourcespace.conf`:

```apache
<VirtualHost *:80>
    ServerName resourcespace.yourdomain.com
    DocumentRoot /var/www/html/resourcespace

    <Directory /var/www/html/resourcespace>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    # Protect sensitive directories
    <Directory /var/www/html/resourcespace/filestore>
        Options -Indexes
        AllowOverride None
        Require all denied
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/resourcespace_error.log
    CustomLog ${APACHE_LOG_DIR}/resourcespace_access.log combined
</VirtualHost>
```

Enable the site and disable the default:

```bash
sudo a2ensite resourcespace.conf
sudo a2dissite 000-default.conf
sudo systemctl reload apache2
```

---

## 8. Create Filestore Directory

ResourceSpace stores all uploaded assets outside the web root for security:

```bash
sudo mkdir -p /var/resourcespace/filestore
sudo chown -R www-data:www-data /var/resourcespace/filestore
sudo chmod -R 775 /var/resourcespace/filestore
```

> You can place this on a separate volume/mount point if needed (e.g., `/mnt/nas/resourcespace`).

---

## 9. Web-Based Installation

Navigate to your server in a browser:

```
http://resourcespace.yourdomain.com/pages/setup.php
```

Fill in the setup form with these values:

| Field | Value |
|---|---|
| MySQL server | `localhost` |
| MySQL database | `resourcespace` |
| MySQL username | `rsuser` |
| MySQL password | *(your password)* |
| MySQL read-only username | *leave blank* |
| MySQL read-only password | *leave blank* |
| Mysql binary path | `/usr/bin/mysql` |
| Application name | ResourceSpace |
| Base URL | http://resourcespace.yourdomain.com |
| Admin full name | Admin user |
| Admin email | *your email* |
| Admin username | admin |
| Admin password | *your password* |
| Email from address | *again your email* |
| ImageMagick Path | `/usr/bin` |
| FFmpeg Path | `/usr/bin` |
| Ghostscript Path | `/usr/bin` |
| Exiftool Path | `/usr/bin` |
| AntiWord Path | *leave blank* |
| PDFtotext Parth | `/usr/bin` |

After completing setup, the installer writes a `config.php` file. Add a line to it and then protect it:

```bash
echo "\$storagedir = '/var/resourcespace/filestore';" | sudo tee -a /var/www/html/resourcespace/include/config.php
sudo chmod 640 /var/www/html/resourcespace/include/config.php
```

---

## 10. Cron Jobs

ResourceSpace uses scheduled tasks for preview generation, indexing, and housekeeping.

Edit the `www-data` crontab:

```bash
sudo crontab -u www-data -e
```

Add:

```cron
# ResourceSpace background tasks — run every 2 minutes
*/2 * * * * /usr/bin/php /var/www/html/resourcespace/pages/process_queued_jobs.php > /dev/null 2>&1

# Daily integrity check and cleanup
0 2 * * * /usr/bin/php /var/www/html/resourcespace/pages/cron_checker.php > /dev/null 2>&1
```

---

## 11. SSL with Let's Encrypt (Recommended)

```bash
sudo apt install -y certbot python3-certbot-apache
sudo certbot --apache -d resourcespace.yourdomain.com
```

Certbot will update your Apache config automatically. Auto-renewal is set up via a systemd timer — verify it:

```bash
sudo systemctl status certbot.timer
```

---

## 12. Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Apache Full'
sudo ufw enable
sudo ufw status
```

---

## 13. Post-Install Hardening

### Restrict config.php

```bash
sudo chmod 640 /var/www/html/resourcespace/include/config.php
sudo chown www-data:www-data /var/www/html/resourcespace/include/config.php
```

### Disable PHP expose_version

In `/etc/php/8.1/apache2/php.ini`:

```ini
expose_php = Off
```

### Remove setup.php after installation

```bash
sudo rm /var/www/html/resourcespace/pages/setup.php
```

### Apache security headers

Add to your virtual host config inside `<VirtualHost>`:

```apache
Header always set X-Content-Type-Options "nosniff"
Header always set X-Frame-Options "SAMEORIGIN"
Header always set X-XSS-Protection "1; mode=block"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
```

---

## 14. Optional: SMTP Email

Edit `/var/www/html/resourcespace/include/config.php` and add:

```php
$email_from        = 'noreply@yourdomain.com';
$email_notify      = 'admin@yourdomain.com';
$use_phpmailer     = true;
$phpmailer_host    = 'smtp.yourdomain.com';
$phpmailer_port    = 587;
$phpmailer_auth    = true;
$phpmailer_username = 'smtp_user';
$phpmailer_password = 'smtp_password';
$phpmailer_secure  = 'tls';
```

---

## 15. Optional: LDAP / Active Directory

In `config.php`:

```php
$ldap_auth        = true;
$ldap_server      = 'ldap://your-ldap-server';
$ldap_binddn      = 'cn=binduser,dc=example,dc=com';
$ldap_bindpw      = 'bindpassword';
$ldap_dn          = 'dc=example,dc=com';
$ldap_filter      = '(sAMAccountName=%s)';
```

---

## Troubleshooting

**Blank page / 500 error**
```bash
sudo tail -f /var/log/apache2/resourcespace_error.log
sudo tail -f /var/log/php8.1-fpm.log  # if using FPM
```

**Thumbnails not generating**
- Confirm `www-data` can execute `convert`, `ffmpeg`, `gs`
- Check ImageMagick PDF policy (Section 5)
- Verify filestore permissions: `ls -la /var/resourcespace/filestore`

**Database connection refused**
```bash
sudo systemctl status mysql
mysql -u rsuser -p resourcespace
```

**Upload size limit**
- Check both `upload_max_filesize` and `post_max_size` in `php.ini`
- Restart Apache after changes: `sudo systemctl restart apache2`

**Permissions reset helper**
```bash
sudo chown -R www-data:www-data /var/www/html/resourcespace
sudo chown -R www-data:www-data /var/resourcespace/filestore
sudo find /var/www/html/resourcespace -type d -exec chmod 755 {} \;
sudo find /var/www/html/resourcespace -type f -exec chmod 644 {} \;
sudo chmod 775 /var/resourcespace/filestore
```

---

## Summary Checklist

- [ ] Ubuntu 22.04 updated
- [ ] Apache installed and configured
- [ ] PHP 8.1 installed with all extensions
- [ ] MySQL database and user created
- [ ] ImageMagick, FFmpeg, Ghostscript, Exiftool installed
- [ ] ImageMagick PDF policy patched
- [ ] ResourceSpace downloaded and extracted
- [ ] Filestore directory created with correct permissions
- [ ] Virtual host configured and enabled
- [ ] Web installer completed at `/pages/setup.php`
- [ ] `setup.php` removed post-install
- [ ] Cron jobs added for `www-data`
- [ ] SSL certificate issued
- [ ] Firewall enabled
- [ ] Security headers configured
