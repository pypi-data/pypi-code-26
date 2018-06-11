from django.core.management import BaseCommand
from scylla_sessions.sessions import (
    get_connection, session_keyspace, session_table
)


class Command(BaseCommand):
    help = "deletes all records in session table if it exist"

    def handle(self, *args, **options):
        scylla_connection = get_connection()
        query = 'TRUNCATE {keyspace}.{table};'.\
            format(keyspace=session_keyspace, table=session_table)
        scylla_connection.execute(query)
