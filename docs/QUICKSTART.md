# Quick Start Guide - SAML IdP Provider

## 🚀 Getting Started in 3 Steps

### Step 1: Create a Superuser

```bash
uv run python manage.py createsuperuser
```

Enter your email, username, and password when prompted.

### Step 2: Start the Development Server

```bash
uv run python manage.py runserver
```

### Step 3: Access the Application

- **Home Page**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Login**: http://localhost:8000/accounts/login
- **IdP Metadata**: http://localhost:8000/saml2idp/metadata/

## 📋 SAML IdP Endpoints

### Identity Provider Metadata
```
URL: http://localhost:8000/saml2idp/metadata/
Description: Returns the IdP's SAML metadata in XML format
```

### Single Sign-On (SSO) Endpoints
```
POST Binding:    http://localhost:8000/saml2/idp/sso/post
Redirect Binding: http://localhost:8000/saml2/idp/sso/redirect
```

### Single Logout (SLO) Endpoints
```
POST Binding:    http://localhost:8000/saml2/idp/slo/post
Redirect Binding: http://localhost:8000/saml2/idp/slo/redirect
```

## 🔗 Integrating a Service Provider (SP)

### Option 1: Add SP Metadata File

1. Get the SP's metadata XML file
2. Add it to `idp_provider/metadata.xml` (or create separate files)
3. Update the settings if needed

### Option 2: Generate SP Template

```bash
uv run python manage.py generate_sp_metadata \
  --entity-id http://localhost:9000/sp/metadata/ \
  --acs-url http://localhost:9000/sp/acs/ \
  --slo-url http://localhost:9000/sp/slo/ \
  --output sp_metadata.xml
```

## 🧪 Testing the IdP

### Test with a SAML SP

Example SP configuration:

```json
{
  "idp_metadata_url": "http://localhost:8000/saml2idp/metadata/",
  "idp_sso_url": "http://localhost:8000/saml2/idp/sso/post",
  "idp_slo_url": "http://localhost:8000/saml2/idp/slo/post",
  "idp_entity_id": "http://localhost:8000/saml2/idp/metadata/"
}
```

### Using SAML Chrome/Firefox Extension

1. Install "SAML Tracer" browser extension
2. Configure your SP to use this IdP
3. Initiate SSO from the SP
4. Monitor SAML requests/responses in the tracer

## 📊 User Attributes Sent to SP

The following user attributes are mapped to SAML attributes:

| Django Field | SAML Attribute Name | OID |
|-------------|---------------------|-----|
| email | email | urn:oid:0.9.2342.19200300.100.1.3 |
| username | username | urn:oid:0.9.2342.19200300.100.1.1 |
| first_name | first_name | urn:oid:2.5.4.42 |
| last_name | last_name | urn:oid:2.5.4.4 |

Additional attributes available via custom processors:
- groups
- is_staff
- is_active
- is_superuser
- date_joined
- last_login

## 🔧 Common Tasks

### View IdP Metadata in Browser

```bash
curl http://localhost:8000/saml2idp/metadata/
```

### Create Test Users

```bash
# Via command line
uv run python manage.py shell

# In Python shell
from users.models import User
User.objects.create_user(
    email='test@example.com',
    username='testuser',
    password='testpass123',
    first_name='Test',
    last_name='User'
)
```

### Check SAML Configuration

```bash
uv run python manage.py shell
from django.conf import settings
import json
print(json.dumps(settings.SAML_IDP_CONFIG, indent=2, default=str))
```

### Regenerate Certificates (if needed)

```bash
# Backup old certificates
mv certificates/idp_public_cert.pem certificates/idp_public_cert.pem.backup
mv certificates/idp_private_key.pem certificates/idp_private_key.pem.backup

# Generate new certificates
openssl req -new -x509 -days 3650 -nodes \
  -out certificates/idp_public_cert.pem \
  -keyout certificates/idp_private_key.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

## 🐛 Troubleshooting

### Issue: "xmlsec1 not found"
```bash
# Ubuntu/Debian
sudo apt-get install xmlsec1

# macOS
brew install libxmlsec1
```

### Issue: Database connection error
```bash
# Check .env file
cat .env

# Test MySQL connection
mysql -u root -p
```

### Issue: Certificate errors
```bash
# Verify certificate
openssl x509 -in certificates/idp_public_cert.pem -text -noout

# Verify key
openssl rsa -in certificates/idp_private_key.pem -check
```

## 📚 Additional Resources

- **Full Documentation**: See README.md
- **Django Docs**: https://docs.djangoproject.com/
- **SAML 2.0 Spec**: https://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html
- **pysaml2 Docs**: https://pysaml2.readthedocs.io/
- **djangosaml2idp**: https://github.com/OTA-Insight/djangosaml2idp

## 🎯 Next Steps

1. ✅ Test the IdP with a sample SP
2. ✅ Configure additional attribute processors
3. ✅ Set up production certificates
4. ✅ Configure multiple SPs
5. ✅ Enable SLO (Single Logout)
6. ✅ Deploy to production with HTTPS
