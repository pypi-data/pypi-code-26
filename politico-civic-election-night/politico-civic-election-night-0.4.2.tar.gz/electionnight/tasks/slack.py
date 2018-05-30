import time
from argparse import Namespace

from celery import shared_task
from django.conf import settings
from slacker import Slacker

SLACK_TOKEN = getattr(settings, 'CIVIC_SLACK_TOKEN', None)


def get_client():
    if SLACK_TOKEN:
        return Slacker(SLACK_TOKEN)
    return None


@shared_task
def call_race_in_slack(payload):
    payload = Namespace(**payload)

    if payload.runoff:
        WINNING = '{} will advance to a runoff.'.format(payload.candidate)
    else:
        WINNING = '{} declared winner.'.format(payload.candidate)

    attachment_data = [{
        'fallback': '🚨 RACE CALLED IN {}'.format(payload.division.upper()),
        'color': '#6DA9CC',
        "pretext": '<!here|here> :rotating_light: RACE CALLED IN {}'.format(
            payload.division.upper()
        ),
        'mrkdwn_in': ['fields'],
        "author_name": "Election Bot",
        "author_icon": "https://pbs.twimg.com/profile_images/998954486205898753/gbb2psb__400x400.jpg",  # noqa
        "title": payload.office,
        "text": WINNING,
        "footer": "Associated Press",
        "fields": [
            {
                "title": "Winning vote",
                "value": "*{}%* | _{} votes_".format(
                    payload.vote_percent,
                    payload.vote_count
                ),
                "short": True
            },
            {
                "title": "Precincts reporting",
                "value": "{}%".format(payload.precincts_reporting_percent),
                "short": True
            }
        ],
        'ts': int(time.time())
    }]

    client = get_client()

    client.chat.post_message(
        '#elections-bot',
        '',
        attachments=attachment_data,
        as_user=False,
        username='Elections Bot'
    )
