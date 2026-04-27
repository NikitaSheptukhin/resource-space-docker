# ResourceSpace with Active Directory / LDAP Authentication

## How ResourceSpace Handles LDAP

ResourceSpace has **built-in LDAP support**. When enabled, it delegates authentication to your AD/LDAP server — users log in with their domain credentials, and ResourceSpace either auto-creates their account on first login or maps them to an existing one. Local ResourceSpace passwords are bypassed for LDAP users.

---

## Core Configuration

All LDAP settings go in `config/config.php`:

```php
// Enable LDAP authentication
$ldap_auth = true;

// Your AD/LDAP server
$ldap_server = "ldap://192.168.1.10";          // or ldaps:// for SSL
$ldap_port   = 389;                             // 636 for LDAPS

// The base DN to search for users
$ldap_base_dn = "DC=yourdomain,DC=local";

// A service account used to bind and search the directory
$ldap_bind_username = "CN=svc-resourcespace,OU=Service Accounts,DC=yourdomain,DC=local";
$ldap_bind_password = "serviceaccountpassword";

// The attribute that matches what the user types as their username
$ldap_username_field = "sAMAccountName";        // standard for Active Directory
                                                // use "uid" for OpenLDAP

// Where to search for users
$ldap_dn = "OU=Users,DC=yourdomain,DC=local";
```

---

## Active Directory Specific Settings

AD has some quirks compared to vanilla LDAP:

```php
// AD requires the full UPN or DN to bind in some configurations
// If simple bind fails, try:
$ldap_bind_username = "svc-resourcespace@yourdomain.local";  // UPN format

// Filter to restrict which AD users can log in
// This restricts login to members of a specific group
$ldap_filter = "(&(objectClass=user)(memberOf=CN=ResourceSpace Users,OU=Groups,DC=yourdomain,DC=local))";

// If not filtering by group, a basic filter for enabled AD user accounts:
$ldap_filter = "(&(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))";
```

---

## LDAPS / SSL Connections

If your AD requires encrypted connections (recommended):

```php
$ldap_server = "ldaps://192.168.1.10";
$ldap_port   = 636;
```

You also need to configure the LDAP client on the **web server** to trust your AD's certificate. On Linux, add your CA cert and update:

```bash
# Add your domain CA cert
cp yourdomain-ca.crt /usr/local/share/ca-certificates/
update-ca-certificates

# Tell the LDAP client not to enforce cert verification during testing (not for production)
# In /etc/ldap/ldap.conf:
TLS_REQCERT never   # testing only
TLS_REQCERT demand  # production with valid cert
```

---

## User Account Behaviour

**Auto-creation on first login:**

```php
// Automatically create a ResourceSpace account when an LDAP user logs in for the first time
$ldap_create_user = true;

// Default user group assigned to auto-created LDAP users
// Get the group ID from the ResourceSpace admin panel (Admin > User Management > Groups)
$ldap_default_group = 2;
```

**Attribute mapping** — pull AD attributes into ResourceSpace user fields:

```php
// Map AD attributes to ResourceSpace user profile fields
$ldap_name_field  = "displayName";   // shown as the user's full name
$ldap_email_field = "mail";          // user's email address
```

---

## Group Synchronisation (Optional)

ResourceSpace doesn't have native AD group → RS group sync out of the box, but you can control access by:

1. **Filtering at login** — use `$ldap_filter` to allow only members of a specific AD group to authenticate at all (shown above)
2. **Manual group assignment** — LDAP users are auto-created and placed in `$ldap_default_group`; admins can then move them to appropriate RS groups
3. **Custom plugin** — for full dynamic group mapping, a custom RS plugin can query AD group membership at login and assign RS groups accordingly

---

## Service Account Requirements

The bind/service account (`svc-resourcespace`) needs the following AD permissions — nothing elevated:

- **Read** access to the user objects in the search base OU
- **List Contents** on the OUs being searched
- The account should be set to **Password never expires** and **User cannot change password**
- Place it in a dedicated **Service Accounts** OU and apply a fine-grained password policy if your domain uses them

---

## Testing the Connection

Before going live, test your LDAP connection from the ResourceSpace server:

```bash
# Test basic connectivity
ldapsearch -H ldap://192.168.1.10 -D "svc-resourcespace@yourdomain.local" \
  -w "password" -b "DC=yourdomain,DC=local" "(sAMAccountName=testuser)"

# If ldapsearch isn't installed
apt install ldap-utils
```

A successful response returns the user's attributes. Common failure reasons:

| Error | Likely Cause |
|---|---|
| `Can't contact LDAP server` | Firewall blocking port 389/636, or wrong IP |
| `Invalid credentials` | Wrong bind DN format or password |
| `No such object` | Wrong base DN |
| `Referral` | Need to search a parent OU or use GC port 3268 |

---

## Using the Global Catalog (Large AD Environments)

If your AD has multiple domains or a complex forest, point at the **Global Catalog** instead:

```php
$ldap_server = "ldap://192.168.1.10";
$ldap_port   = 3268;   // GC port (3269 for LDAPS)
$ldap_base_dn = "DC=yourdomain,DC=local";  // forest root
```

This lets you search across all domains in the forest in a single query.

---

## Mixed Authentication (LDAP + Local Accounts)

ResourceSpace supports having both LDAP users and local accounts simultaneously. Local admin accounts (like the built-in `admin`) will continue to use ResourceSpace's own password system, while other users authenticate via LDAP. This means:

- Always keep at least one **local admin account** as a fallback in case the LDAP server is unreachable
- LDAP users who are manually given a local password can fall back to local auth if needed, depending on configuration
