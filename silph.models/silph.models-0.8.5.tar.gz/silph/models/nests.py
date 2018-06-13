
from asyncqlio import (
    Column,
    Integer,
    SmallInt,
    String,
    Text,
    Timestamp,
    Serial,
    Boolean,
    Numeric,
)

from .base import Table


class Nest(Table, table_name='nests'):
    id = Column(Serial, primary_key=True, unique=True)

    original_pokemon = Column.with_name('pokemon_id', Integer, nullable=False)
    pokemon = Column.with_name('current_species', Integer, nullable=False)

    user = Column.with_name('user_id', Integer, nullable=False)

    latitude = Column(Numeric(8, 12), nullable=False)
    longitude = Column(Numeric(8, 12), nullable=False)

    spotted = Column.with_name('avg_spotted_count', Numeric(0, 3))
    visit_duration = Column.with_name('avg_visit_duration', Integer)
    rating = Column.with_name('avg_location_rating', SmallInt)

    cluster = Column.with_name('is_cluster', Boolean, default=False, nullable=False)
    repeater = Column.with_name('is_repeater', Boolean, default=False, nullable=False)

    status = Column(SmallInt, nullable=False)
    spawn_type = Column(SmallInt, nullable=False)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)


class NestVerification(Table, table_name='nest_verifications'):
    id = Column(Serial, primary_key=True, unique=True)


class NestAdvice(Table, table_name='nest_advices'):
    id = Column(Serial, primary_key=True, unique=True)


class NestMigration(Table, table_name='nest_migrations'):
    id = Column(Serial, primary_key=True, unique=True)
