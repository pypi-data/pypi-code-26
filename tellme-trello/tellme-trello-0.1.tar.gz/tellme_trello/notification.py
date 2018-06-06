import warnings
from django.template.defaultfilters import truncatechars
from django.utils.translation import ugettext_lazy as _
from tellme_trello import settings
from tellme_trello.client import get_client


def create_ticket(request, feedback, fail_silently=True):
    try:
        client = get_client()
        list_ = client.get_list(settings.LIST_ID)
        card = list_.add_card(
            name=truncatechars(feedback.comment, 200),
            desc=feedback.comment)
        card.attach(
            name='screenshot.png',
            mimeType='image/png',
            file=feedback.screenshot.file)
    except Exception as err:
        if not fail_silently:
            raise
        warnings.warn("Trello notification doesn't work: %s" % err)
