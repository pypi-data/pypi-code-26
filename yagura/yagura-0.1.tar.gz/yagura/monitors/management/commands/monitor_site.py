from uuid import UUID
from django.core.management.base import BaseCommand, CommandError
from yagura.sites.models import Site
from yagura.monitors import services


class Command(BaseCommand):
    help = 'monitor specified website'

    def add_arguments(self, parser):
        parser.add_argument('site_id', type=str)

    def handle(self, *args, **options):
        site_id = options['site_id']
        try:
            UUID(site_id)
        except ValueError:
            raise CommandError(f"Argument must be UUID")
        try:
            site = Site.objects.get(pk=site_id)
            # TODO: Implement it
            target = site.targets.first()
            result = services.try_monitor(target.site.url)
            if result == 'OK':
                self.stdout.write(
                    self.style.SUCCESS('OK'))
            else:
                self.stdout.write(
                    self.style.ERROR('NG'))
            services.save_state(target, result)
        except Site.DoesNotExist:
            raise CommandError(f"Site is not found")
