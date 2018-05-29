from sqlite3 import OperationalError

from sqlite_framework.component.component import SqliteStorageComponent
from sqlite_framework.sql.item.column import Column
from sqlite_framework.sql.item.constants.conflict_resolution import REPLACE
from sqlite_framework.sql.item.constants.operator import EQUAL
from sqlite_framework.sql.item.constants.type import TEXT, INTEGER
from sqlite_framework.sql.item.constraint.column.simple import PRIMARY_KEY, NOT_NULL
from sqlite_framework.sql.item.expression.compound.condition import Condition
from sqlite_framework.sql.item.table import Table
from sqlite_framework.sql.statement.builder.insert import Insert
from sqlite_framework.sql.statement.builder.select import Select


NAME = "version_info"
VERSION = 1


COMPONENT = Column("component", TEXT, PRIMARY_KEY, NOT_NULL)
COMPONENT_VERSION = Column("version", INTEGER)


VERSION_INFO = Table("version_info")
VERSION_INFO.column(COMPONENT)
VERSION_INFO.column(COMPONENT_VERSION)


SET_VERSION = Insert().or_(REPLACE)\
    .table(VERSION_INFO)\
    .columns(COMPONENT, COMPONENT_VERSION)\
    .values(":component", ":version")\
    .build()

GET_VERSION = Select()\
    .fields(COMPONENT_VERSION)\
    .table(VERSION_INFO)\
    .where(Condition(COMPONENT, EQUAL, ":component"))\
    .build()


class VersionInfoSqliteComponent(SqliteStorageComponent):
    """
    Take special care with updating the version of this component,
    as its migrations may be problematic.
    To avoid errors, they should be as direct as possible.
    """

    def __init__(self):
        super().__init__(NAME, VERSION)
        self.managed_tables(VERSION_INFO)
        self.migrated = False

    def create(self):
        super().create()
        self.migrated = True

    def set_version(self, component: str, version: int):
        self.statement(SET_VERSION).execute(component=component, version=version)

    def get_version(self, component: str):
        try:
            row = self.statement(GET_VERSION).execute(component=component).first()
        except OperationalError as e:
            if component == self.name and not self.migrated:
                # if the version of this module is being checked and it has not yet being migrated
                # it could fail as the table may not yet exist or have a different schema
                row = None
            else:
                # if the error is for another reason, let it propagate
                raise e
        if row is not None:
            return row[COMPONENT_VERSION]
