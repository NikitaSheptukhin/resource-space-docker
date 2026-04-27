# Questions about currrent LDAP setup

This is a list of questions we need answered to know how to integrate LDAP. 
Any question which asks for confirmation about resourcespace's integration with LDAP are to be answered true or false on whether or not the integration would even be allowed.

## Server Details

- What is the IP address or hostname of the LDAP/AD server?
- What port is LDAP running on — standard 389, or LDAPS on 636?
- Is SSL/TLS required for LDAP connections, and if so can you provide the CA certificate?
- Is this a single domain or a multi-domain forest (which would require the Global Catalog on port 3268)?

## Structure & Schema

- What is the base DN of the domain? (e.g. DC=company,DC=local)
- Which OU contains the user accounts that need access to ResourceSpace?
- Is sAMAccountName the login attribute, or do users log in with something else like their email (UPN)?
- What attribute holds the user's full name — is it displayName or cn?
- What attribute holds the user's email — is it mail?

## Service Account

- Can you create a dedicated read-only service account for ResourceSpace to bind with?
- What will the full DN or UPN of that account be?
- Can it be set to password never expires, since ResourceSpace needs it to be always available?

## Network & Firewall

- Is the ResourceSpace web server allowed to reach the AD server on port 389/636?
- Are there any firewall rules or network segments that would block that traffic?
- Is the LDAP server accessible from the subnet where ResourceSpace will be hosted?

## Passwords & Policy

- Does the domain enforce password expiry — and will that affect the service account?
- Is there an account lockout policy that could lock the service account if ResourceSpace misconfigures the bind credentials?
