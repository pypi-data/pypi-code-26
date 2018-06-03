from django.core.management.base import BaseCommand
from yagura.sites.models import Site
from yagura.monitors import services


class Command(BaseCommand):
    help = 'monitor all websites'

    def handle(self, *args, **options):
        for site in Site.objects.all():
            target = site.targets.first()
            result = services.try_monitor(target.site.url)
            if result == 'OK':
                self.stdout.write(
                    self.style.SUCCESS('OK'))
            else:
                self.stdout.write(
                    self.style.ERROR('NG'))
            services.save_state(target, result)
