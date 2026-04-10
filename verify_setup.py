"""
SAML IdP Setup Verification Script

This script checks if all components required for the SAML IdP are properly configured.
"""

import os
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} NOT FOUND: {filepath}")
        return False


def check_command_available(command_name):
    """Check if a command is available in PATH."""
    import shutil
    if shutil.which(command_name):
        print(f"✓ {command_name} is available")
        return True
    else:
        print(f"✗ {command_name} NOT FOUND in PATH")
        return False


def main():
    print("=" * 60)
    print("SAML IdP Setup Verification")
    print("=" * 60)
    print()
    
    base_dir = Path(__file__).resolve().parent
    all_checks_passed = True
    
    # Check certificates
    print("\n📜 Certificates:")
    cert_file = base_dir / 'certificates' / 'idp_public_cert.pem'
    key_file = base_dir / 'certificates' / 'idp_private_key.pem'
    all_checks_passed &= check_file_exists(cert_file, "Public certificate")
    all_checks_passed &= check_file_exists(key_file, "Private key")
    
    # Check required files
    print("\n📁 Required Files:")
    required_files = [
        ('manage.py', 'Django manage.py'),
        ('idp_provider/settings.py', 'Settings file'),
        ('idp_provider/urls.py', 'URL configuration'),
        ('idp_provider/metadata.xml', 'SP metadata'),
        ('core/saml_processors.py', 'SAML processors'),
        ('core/views.py', 'Core views'),
        ('users/models.py', 'User model'),
    ]
    
    for filepath, description in required_files:
        full_path = base_dir / filepath
        all_checks_passed &= check_file_exists(full_path, description)
    
    # Check external dependencies
    print("\n🔧 External Dependencies:")
    all_checks_passed &= check_command_available('xmlsec1')
    all_checks_passed &= check_command_available('openssl')
    
    # Check Python packages
    print("\n📦 Python Packages:")
    try:
        import django
        print(f"✓ Django: {django.VERSION}")
    except ImportError:
        print("✗ Django NOT INSTALLED")
        all_checks_passed = False
    
    try:
        import djangosaml2idp
        print(f"✓ djangosaml2idp: installed")
    except ImportError:
        print("✗ djangosaml2idp NOT INSTALLED")
        all_checks_passed = False
    
    try:
        import saml2
        print(f"✓ pysaml2: installed")
    except ImportError:
        print("✗ pysaml2 NOT INSTALLED")
        all_checks_passed = False
    
    try:
        import allauth
        print(f"✓ django-allauth: installed")
    except ImportError:
        print("✗ django-allauth NOT INSTALLED")
        all_checks_passed = False
    
    # Check database configuration
    print("\n🗄️  Database Configuration:")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '3306')
        
        if db_name and db_user and db_password:
            print(f"✓ Database: {db_name}@{db_host}:{db_port}")
            print(f"  User: {db_user}")
        else:
            print("✗ Database configuration incomplete in .env")
            all_checks_passed = False
    except Exception as e:
        print(f"✗ Error loading database config: {e}")
        all_checks_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("✅ All checks passed! Your SAML IdP is ready.")
        print("\nNext steps:")
        print("1. Run: uv run python manage.py createsuperuser")
        print("2. Run: uv run python manage.py runserver")
        print("3. Visit: http://localhost:8000")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install xmlsec1: sudo apt-get install xmlsec1")
        print("- Generate certificates: openssl req -new -x509 ...")
        print("- Install dependencies: uv sync")
        print("- Configure .env file with database credentials")
    print("=" * 60)
    
    return 0 if all_checks_passed else 1


if __name__ == '__main__':
    sys.exit(main())
