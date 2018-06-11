from django.core.management.base import BaseCommand
from gcb_web_auth.models import DDSEndpoint


class Command(BaseCommand):
    help = 'Create/Replace DDSEndpoint in the database.'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Endpoint Name')
        parser.add_argument('api_root', type=str, help='DukeDS API url')
        parser.add_argument('portal_root', type=str, help='DukeDS portal url')
        parser.add_argument('agent_key', type=str, help='Agent key to use when authenticating this application')
        parser.add_argument('openid_provider_id', type=str, help='OpenID provider from DukeDS api/v1/auth_providers')

    def handle(self, *args, **options):
        fields = dict()
        for k in {'name','api_root','portal_root','agent_key','openid_provider_id'}:
            fields[k] = options[k]
        existing = DDSEndpoint.objects.filter(name=fields['name'])
        if existing:
            existing.update(**fields)
        else:
            DDSEndpoint.objects.create(**fields)
