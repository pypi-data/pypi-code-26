from django.core.management import base as management_base
from django.conf import settings
from raven.contrib.django.models import client
from telegram import TelegramError

from bots.bots import dispatchers


class Command(management_base.BaseCommand):
    def handle(self, *args, **options):
        for pk, dispatcher in dispatchers.items():
            try:
                dispatcher.bot.set_webhook(f'https://{settings.WEBHOOK_DOMAIN}/webhook/{pk}/')
            except TelegramError:
                client.captureException()
        print('Webhooks set')
