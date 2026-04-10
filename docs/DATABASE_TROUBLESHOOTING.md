# Database Table Issues & Troubleshooting

This document covers common database table issues you may encounter when setting up the SAML IdP with Google Sign-In, along with their solutions.

## Common Issues

### Issue 1: `socialaccount_socialapp_sites` table doesn't exist

**Error Message:**
```
ProgrammingError at /accounts/login/
(1146, "Table 'idp_provider.socialaccount_socialapp_sites' doesn't exist")
```

**Root Cause:**
The `socialaccount_socialapp_sites` table is a many-to-many through table that links `SocialApp` (Google OAuth config) to `Site` (Django sites framework). This table should be created automatically by Django migrations, but sometimes it doesn't get created due to:

- Migration history conflicts (e.g., `socialaccount` migrations applied before `sites`)
- Incomplete or corrupted migration history
- Manual database restores without proper schema

**Solution:**

Run the following command to create the missing table:

```bash
uv run python manage.py dbshell -- -e "CREATE TABLE socialaccount_socialapp_sites (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, socialapp_id INT NOT NULL, site_id INT NOT NULL, UNIQUE KEY socialaccount_socialapp_sites_socialapp_id_site_id_uniq (socialapp_id, site_id), KEY socialaccount_socialapp_sites_socialapp_id_89c2e975 (socialapp_id), KEY socialaccount_socialapp_sites_site_id_711e367e (site_id), CONSTRAINT socialaccount_socialap_socialapp_id_89c2e975_fk_socialacc FOREIGN KEY (socialapp_id) REFERENCES socialaccount_socialapp (id), CONSTRAINT socialaccount_socialapp_sites_site_id_711e367e_fk_django_site_id FOREIGN KEY (site_id) REFERENCES django_site (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;"
```

**Verify the table exists:**
```bash
uv run python manage.py dbshell -- -e "SHOW TABLES LIKE 'socialaccount_%';"
```

Expected output:
```
+------------------------------------------+
| Tables_in_idp_provider (socialaccount_%) |
+------------------------------------------+
| socialaccount_socialaccount              |
| socialaccount_socialapp                  |
| socialaccount_socialapp_sites            |
| socialaccount_socialtoken                |
+------------------------------------------+
```

---

### Issue 2: `django_site` table doesn't exist

**Error Message:**
```
ProgrammingError: (1146, "Table 'idp_provider.django_site' doesn't exist")
```

**Root Cause:**
The Django sites framework table (`django_site`) was never created, even though the migration was recorded. This can happen when:

- The `django.contrib.sites` app was added after initial migrations
- Migration was faked without actually creating the table
- Database was restored from a backup that excluded this table

**Solution:**

1. **Create the table manually:**
```bash
uv run python manage.py dbshell -- -e "CREATE TABLE IF NOT EXISTS django_site (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, domain VARCHAR(100) NOT NULL, name VARCHAR(50) NOT NULL); INSERT INTO django_site (id, domain, name) VALUES (1, 'localhost:8000', 'SAML IdP Provider') ON DUPLICATE KEY UPDATE domain='localhost:8000', name='SAML IdP Provider';"
```

2. **Ensure migration is recorded:**
```bash
uv run python manage.py dbshell -- -e "INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('sites', '0001_initial', NOW()), ('sites', '0002_alter_domain_unique', NOW());"
```

3. **Verify the table exists:**
```bash
uv run python manage.py dbshell -- -e "SELECT * FROM django_site;"
```

Expected output:
```
+----+----------------+-----------------+
| id | domain         | name            |
+----+----------------+-----------------+
|  1 | localhost:8000 | SAML IdP Provider |
+----+----------------+-----------------+
```

---

### Issue 3: Migration dependency conflicts

**Error Message:**
```
django.db.migrations.exceptions.InconsistentMigrationHistory: 
Migration socialaccount.0001_initial is applied before its dependency sites.0001_initial on database 'default'.
```

**Root Cause:**
This happens when `socialaccount` migrations were applied before `sites` migrations, but `socialaccount` depends on `sites`. Django's migration system detects this inconsistent history and refuses to proceed.

**Solution:**

1. **Check current migration history:**
```bash
uv run python manage.py dbshell -- -e "SELECT app, name FROM django_migrations WHERE app IN ('sites', 'socialaccount', 'account') ORDER BY app, id;"
```

2. **If `sites` migrations are missing, add them:**
```bash
uv run python manage.py dbshell -- -e "INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('sites', '0001_initial', NOW()), ('sites', '0002_alter_domain_unique', NOW());"
```

3. **If the tables are also missing, create them first** (see Issue 2 above)

4. **Then run migrations:**
```bash
uv run python manage.py migrate
```

---

### Issue 4: Missing `jwt` module

**Error Message:**
```
ModuleNotFoundError: No module named 'jwt'
```

**Root Cause:**
The `pyjwt` package is required by `django-allauth` for Google OAuth2 JWT token handling but wasn't installed.

**Solution:**

```bash
uv add pyjwt>=2.8.0
uv sync
```

Or manually add to `pyproject.toml`:
```toml
dependencies = [
    # ...
    "pyjwt>=2.8.0",
]
```

Then run:
```bash
uv sync
```

---

## Preventive Measures

### 1. Install all dependencies from the start

```bash
uv sync
```

This ensures all packages in `pyproject.toml` are installed, including:
- `pyjwt` - For Google OAuth2
- `pysaml2` - For SAML protocol
- `djangosaml2idp` - For Django IdP integration

### 2. Run migrations in order

```bash
# First, ensure all apps are in INSTALLED_APPS
uv run python manage.py migrate
```

If you encounter dependency issues, you can run migrations for specific apps first:

```bash
uv run python manage.py migrate contenttypes
uv run python manage.py migrate auth
uv run python manage.py migrate sites
uv run python manage.py migrate socialaccount
uv run python manage.py migrate account
uv run python manage.py migrate
```

### 3. Verify your database schema

After running migrations, verify all required tables exist:

```bash
# Check all Django tables
uv run python manage.py dbshell -- -e "SHOW TABLES;"

# Check specific socialaccount tables
uv run python manage.py dbshell -- -e "SHOW TABLES LIKE 'socialaccount_%';"

# Check sites table
uv run python manage.py dbshell -- -e "SHOW TABLES LIKE 'django_site';"
```

### 4. Use the verification script

```bash
uv run python verify_setup.py
```

This checks certificates, dependencies, and database configuration.

---

## Database Schema Reference

### Required Tables for Google Sign-In

| Table Name | Purpose |
|-----------|---------|
| `django_site` | Django sites framework (required by allauth) |
| `socialaccount_socialapp` | Stores OAuth app configurations (Google, GitHub, etc.) |
| `socialaccount_socialapp_sites` | Many-to-many linking table between apps and sites |
| `socialaccount_socialaccount` | User's social accounts linked to their profile |
| `socialaccount_socialtoken` | OAuth tokens for social accounts |
| `account_emailaddress` | User email addresses and verification status |

### Table Relationships

```
django_site (1) ←→ (M) socialaccount_socialapp_sites (M) ←→ (1) socialaccount_socialapp
                                                                        ↓
                                                            socialaccount_socialaccount
                                                                        ↓
                                                               users.User (custom user)
```

---

## Emergency Reset (Last Resort)

If your database is in a broken state and you can't fix it with the steps above, you can reset all migrations:

⚠️ **WARNING: This will delete all data!**

```bash
# 1. Drop all socialaccount and sites tables
uv run python manage.py dbshell -- -e "DROP TABLE IF EXISTS socialaccount_socialapp_sites, socialaccount_socialtoken, socialaccount_socialaccount, socialaccount_socialapp, django_site;"

# 2. Remove migration records
uv run python manage.py dbshell -- -e "DELETE FROM django_migrations WHERE app IN ('sites', 'socialaccount', 'account');"

# 3. Recreate tables via migrations
uv run python manage.py migrate sites
uv run python manage.py migrate socialaccount
uv run python manage.py migrate account
uv run python manage.py migrate

# 4. Insert default site
uv run python manage.py dbshell -- -e "INSERT INTO django_site (id, domain, name) VALUES (1, 'localhost:8000', 'SAML IdP Provider');"
```

---

## Quick Reference Commands

### Check if a table exists
```bash
uv run python manage.py dbshell -- -e "SHOW TABLES LIKE 'table_name';"
```

### View table structure
```bash
uv run python manage.py dbshell -- -e "SHOW CREATE TABLE table_name\G"
```

### View migration history
```bash
uv run python manage.py dbshell -- -e "SELECT app, name, applied FROM django_migrations ORDER BY id DESC LIMIT 20;"
```

### Check for missing migrations
```bash
uv run python manage.py showmigrations
```

### Fake a migration (mark as applied without running)
```bash
uv run python manage.py migrate app_name migration_name --fake
```

### Revert a migration
```bash
uv run python manage.py migrate app_name previous_migration_name
```

---

## Getting Help

If you encounter an issue not covered here:

1. **Check Django migration status:**
   ```bash
   uv run python manage.py showmigrations
   ```

2. **View the full error traceback** - it usually indicates which table or migration failed

3. **Check your database directly:**
   ```bash
   uv run python manage.py dbshell
   ```

4. **Review migration files** in:
   - `.venv/lib/python3.14/site-packages/allauth/socialaccount/migrations/`
   - `.venv/lib/python3.14/site-packages/django/contrib/sites/migrations/`

5. **Consult Django docs:**
   - Migrations: https://docs.djangoproject.com/en/stable/topics/migrations/
   - Sites framework: https://docs.djangoproject.com/en/stable/ref/contrib/sites/
   - Allauth: https://docs.allauth.org/en/latest/
