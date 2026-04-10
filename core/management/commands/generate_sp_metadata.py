"""
Management command to generate Service Provider metadata template.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Generate Service Provider metadata template'

    def add_arguments(self, parser):
        parser.add_argument(
            '--entity-id',
            type=str,
            default='http://localhost:9000/sp/metadata/',
            help='SP Entity ID (default: http://localhost:9000/sp/metadata/)',
        )
        parser.add_argument(
            '--acs-url',
            type=str,
            default='http://localhost:9000/sp/acs/',
            help='Assertion Consumer Service URL (default: http://localhost:9000/sp/acs/)',
        )
        parser.add_argument(
            '--slo-url',
            type=str,
            default='http://localhost:9000/sp/slo/',
            help='Single Logout Service URL (default: http://localhost:9000/sp/slo/)',
        )
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='Output file path (default: prints to stdout)',
        )

    def handle(self, *args, **options):
        entity_id = options['entity_id']
        acs_url = options['acs_url']
        slo_url = options['slo_url']
        output_file = options['output']

        metadata_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
                     entityID="{entity_id}">
    <md:SPSSODescriptor AuthnRequestsSigned="false" WantAssertionsSigned="true"
                        protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <md:NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress</md:NameIDFormat>
        <md:NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:persistent</md:NameIDFormat>
        <md:NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</md:NameIDFormat>
        
        <md:AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                                     Location="{acs_url}"
                                     index="0"
                                     isDefault="true"/>
        <md:AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
                                     Location="{acs_url}"
                                     index="1"/>
        
        <md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                                Location="{slo_url}"/>
        <md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
                                Location="{slo_url}"/>
    </md:SPSSODescriptor>
</md:EntityDescriptor>'''

        if output_file:
            os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(metadata_xml)
            self.stdout.write(self.style.SUCCESS(f'SP metadata written to: {output_file}'))
        else:
            self.stdout.write(metadata_xml)

        self.stdout.write(self.style.SUCCESS(f'\nSP Entity ID: {entity_id}'))
        self.stdout.write(self.style.SUCCESS(f'ACS URL: {acs_url}'))
        self.stdout.write(self.style.SUCCESS(f'SLO URL: {slo_url}'))
