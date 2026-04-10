# Django SAML 2.0 Identity Provider (IdP)

A Django-based SAML 2.0 Identity Provider (IdP) that enables Single Sign-On (SSO) authentication for Service Providers (SPs).

## Features

- ✅ SAML 2.0 Identity Provider implementation
- ✅ **Google Sign-In** (OAuth 2.0) integration
- ✅ Single Sign-On (SSO) support (POST and Redirect bindings)
- ✅ Single Logout (SLO) support
- ✅ Custom user model with email-based authentication
- ✅ Attribute mapping and custom processors
- ✅ Django admin integration
- ✅ REST API ready
- ✅ Self-signed certificates for development

## Tech Stack

- **Django 6.0+** - Web framework
- **djangosaml2idp** - SAML IdP library for Django
- **pysaml2** - Python SAML 2.0 implementation
- **django-allauth** - Authentication management (Email + Google OAuth2)
- **PyJWT** - JWT handling for Google OAuth2
- **MySQL** - Database
- **xmlsec1** - XML signature verification

## Prerequisites

- Python 3.14+
- MySQL 5.7+ or 8.0+
- `xmlsec1` binary installed on the system
- OpenSSL (for certificate generation)

## Installation

### 1. Install Dependencies

```bash
# Install xmlsec1 (required for SAML signing)
# Ubuntu/Debian:
sudo apt-get install xmlsec1

# macOS:
brew install libxmlsec1

# Install Python dependencies
uv sync
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and update:

```env
# Database
DB_NAME=idp_provider_db
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# Google OAuth2 (Optional - for Google Sign-In)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

**Note:** Google Sign-In is optional. The app works without it using email/password authentication. See [GOOGLE_SIGNIN_SETUP.md](GOOGLE_SIGNIN_SETUP.md) for detailed setup instructions.

### 3. Database Setup

Create a MySQL database:

```sql
CREATE DATABASE idp_provider_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Run Migrations

```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

### 5. Generate Certificates (Optional - already provided for dev)

For production, generate your own certificates:

```bash
openssl req -new -x509 -days 3650 -nodes \
  -out certificates/idp_public_cert.pem \
  -keyout certificates/idp_private_key.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=idp.example.com"
```

## Running the Server

```bash
uv run python manage.py runserver
```

The IdP will be available at `http://localhost:8000`

## SAML IdP Endpoints

### Core Endpoints

| Endpoint | Description |
|----------|-------------|
| `http://localhost:8000/` | Home page |
| `http://localhost:8000/admin/` | Django admin |
| `http://localhost:8000/accounts/login/` | User login |
| `http://localhost:8000/accounts/logout/` | User logout |

### SAML 2.0 Endpoints

| Endpoint | Description |
|----------|-------------|
| `http://localhost:8000/saml2idp/metadata/` | IdP metadata (XML) |
| `http://localhost:8000/saml2/idp/sso/post` | SSO endpoint (POST binding) |
| `http://localhost:8000/saml2/idp/sso/redirect` | SSO endpoint (Redirect binding) |
| `http://localhost:8000/saml2/idp/slo/post` | SLO endpoint (POST binding) |
| `http://localhost:8000/saml2/idp/slo/redirect` | SLO endpoint (Redirect binding) |

## IdP Configuration

### Entity ID
```
http://localhost:8000/saml2/idp/metadata/
```

### IdP Metadata URL
```
http://localhost:8000/saml2idp/metadata/
```

### Certificates
- **Public Certificate:** `certificates/idp_public_cert.pem`
- **Private Key:** `certificates/idp_private_key.pem`

## Integrating a Service Provider (SP)

### Step 1: Add SP Metadata

Add your SP's metadata to `idp_provider/metadata.xml` or configure SPs dynamically through the database.

### Step 2: Configure Attribute Mapping

Update `SAML_ATTRIBUTE_MAPPING` in `settings.py` to map Django user attributes to SAML attributes:

```python
SAML_ATTRIBUTE_MAPPING = {
    'email': ['email', 'urn:oid:0.9.2342.19200300.100.1.3'],
    'username': ['username', 'urn:oid:0.9.2342.19200300.100.1.1'],
    'first_name': ['first_name', 'urn:oid:2.5.4.42'],
    'last_name': ['last_name', 'urn:oid:2.5.4.4'],
}
```

### Step 3: Use Custom Processors (Optional)

Custom attribute processors are available in `core/saml_processors.py`:

- `user_attributes` - Standard user attributes
- `user_email` - Only email
- `user_full_info` - Comprehensive user information

## Example: Test with a SAML SP

### Using SAML Tracer (Browser Extension)

1. Install SAML Tracer extension (Firefox/Chrome)
2. Configure your SP to use this IdP
3. Initiate SSO from the SP
4. Monitor the SAML request/response flow

### Using a Test SP

Example configuration for a test SP:

```xml
<!-- SP Metadata -->
<EntityDescriptor entityID="http://localhost:9000/sp/metadata/">
    <SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                                 Location="http://localhost:9000/sp/acs/"
                                 index="0"/>
    </SPSSODescriptor>
</EntityDescriptor>
```

## User Model

The app uses a custom user model (`users.User`) with email-based authentication:

```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
```

## Security Considerations

### For Production:

1. **Replace self-signed certificates** with CA-signed certificates
2. **Set `DEBUG = False`** in settings
3. **Use HTTPS** for all SAML endpoints
4. **Update `ALLOWED_HOSTS`** with your domain
5. **Secure `SECRET_KEY`** and store in environment variables
6. **Enable CSRF protection** and security middleware
7. **Implement rate limiting** for login endpoints
8. **Audit attribute mapping** to avoid leaking sensitive data

## Troubleshooting

### xmlsec1 Not Found

Ensure `xmlsec1` is installed and in your PATH:

```bash
which xmlsec1
```

Update the path in `settings.py` if needed:

```python
'xmlsec_binary': '/usr/bin/xmlsec1',
```

### Certificate Errors

Verify certificates are valid and match:

```bash
openssl x509 -in certificates/idp_public_cert.pem -text -noout
openssl rsa -in certificates/idp_private_key.pem -check
```

### Database Connection

Ensure MySQL is running and credentials in `.env` are correct.

## Project Structure

```
idp_provider/
├── certificates/              # SAML certificates
│   ├── idp_public_cert.pem
│   └── idp_private_key.pem
├── core/                      # Main app
│   ├── templates/
│   ├── saml_processors.py    # Custom SAML attribute processors
│   ├── urls.py
│   └── views.py
├── idp_provider/             # Project settings
│   ├── settings.py
│   ├── urls.py
│   ├── config.py
│   └── metadata.xml          # SP metadata
├── users/                     # Custom user model
│   └── models.py
├── manage.py
└── pyproject.toml
```

## Development

### Running Tests

```bash
uv run python manage.py test
```

### Creating Migrations

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### Admin Panel

Access the admin panel at `http://localhost:8000/admin/` to:
- Manage users
- Configure SPs (if using database-based configuration)
- View SAML sessions

## License

MIT License

## Support

For issues or questions, please open an issue on the repository.


