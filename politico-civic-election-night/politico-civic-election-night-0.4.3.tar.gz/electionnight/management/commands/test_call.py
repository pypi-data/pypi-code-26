from django.core.management.base import BaseCommand
from electionnight.celery import call_race_in_slack, call_race_on_twitter


class Command(BaseCommand):
    help = 'Sends a test call to Slack/Twitter bots'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        payload = {
            "race_id": '1391',
            "division": 'Alabama',
            "division_slug": 'alabama',
            "office": 'Alabama U.S. House District 1',
            "candidate": 'Robert Kennedy',
            "primary_party": 'Democrat',
            "vote_percent": 0.5,
            "vote_count": 1000,
            "runoff": False,
            "precincts_reporting_percent": 1.0,
            "jungle": False,
            "runoff_election": False
        }

        call_race_in_slack(payload)
        call_race_on_twitter(payload)