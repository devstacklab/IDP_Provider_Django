from django.db import migrations


def update_site(apps, schema_editor):
    """
    Update the default Site configuration.
    """
    Site = apps.get_model('sites', 'Site')
    
    # Update the default site
    try:
        Site.objects.filter(pk=1).update(
            domain='localhost:8000',
            name='SAML IdP Provider'
        )
    except Exception:
        # Table might not exist, that's OK
        pass


def remove_site_update(apps, schema_editor):
    """Reverse operation - do nothing."""
    pass


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunPython(update_site, remove_site_update),
    ]
