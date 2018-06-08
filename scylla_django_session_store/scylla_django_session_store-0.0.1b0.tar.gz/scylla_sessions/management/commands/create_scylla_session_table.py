from django.core.management import BaseCommand
from scylla_sessions.sessions import (
    get_connection,
    session_keyspace,
    session_table
)


create_session_keyspace = "create keyspace if not exists %s with " \
                          "replication = {" \
                          "'class' : 'SimpleStrategy', " \
                          "'replication_factor' : 3};" % session_keyspace

create_session_table = "create table if not exists {keyspace}.{table} (" \
                       "session_id text, " \
                       "session_data text, " \
                       "updated_at timestamp, " \
                       "primary key (session_id));".format(
                        keyspace=session_keyspace,
                        table=session_table)

create_index_on_update_at = "CREATE INDEX IF NOT EXISTS {keyspace}_update_at_idx ON " \
                            "sessions.sessions (updated_at);".format(keyspace=session_keyspace)


class Command(BaseCommand):
    help = "creates session table if does not exist"

    def handle(self, *args, **options):
        scylla_connection = get_connection()
        scylla_connection.execute(create_session_keyspace)
        scylla_connection.execute(create_session_table)
        scylla_connection.execute(create_index_on_update_at)
