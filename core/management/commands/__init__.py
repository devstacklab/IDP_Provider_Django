from django.db import migrations


def create_site_and_social_app(apps, schema_editor):
    """
    Create the default Site and configure Google social provider.
    The actual Google client_id and secret come from environment variables.
    """
    Site = apps.get_model('sites', 'Site')
    
    # Update or create the default site
    site, created = Site.objects.update_or_create(
        pk=1,
        defaults={
            'domain': 'localhost:8000',
            'name': 'SAML IdP Provider'
        }
    )


def remove_site_and_social_app(apps, schema_editor):
    """Reverse operation - do nothing."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),  # Adjust if you have different initial migration
    ]

    operations = [
        migrations.RunPython(create_site_and_social_app, remove_site_and_social_app),
    ]
