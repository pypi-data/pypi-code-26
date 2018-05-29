from sqlite_framework.component.component import SqliteStorageComponent
from sqlite_framework.sql.item.column import Column
from sqlite_framework.sql.item.constants.conflict_resolution import REPLACE
from sqlite_framework.sql.item.constants.operator import EQUAL, AND
from sqlite_framework.sql.item.constants.order_mode import DESC, ASC
from sqlite_framework.sql.item.constants.type import INTEGER, TEXT
from sqlite_framework.sql.item.constraint.column.default import Default
from sqlite_framework.sql.item.constraint.column.simple import PRIMARY_KEY, NOT_NULL
from sqlite_framework.sql.item.constraint.foreign_key.change import CASCADE
from sqlite_framework.sql.item.constraint.foreign_key.references import References
from sqlite_framework.sql.item.constraint.table.unique import Unique
from sqlite_framework.sql.item.expression.compound.cast import Cast
from sqlite_framework.sql.item.expression.compound.condition import Condition, MultipleCondition
from sqlite_framework.sql.item.expression.constants import CURRENT_UNIX_TIMESTAMP
from sqlite_framework.sql.item.table import Table
from sqlite_framework.sql.result.row import ResultRow
from sqlite_framework.sql.statement.builder.delete import Delete
from sqlite_framework.sql.statement.builder.insert import Insert
from sqlite_framework.sql.statement.builder.select import Select


NAME = "test"
VERSION = 2


ID = Column("id", INTEGER, PRIMARY_KEY, NOT_NULL)
TEXT_COLUMN = Column("text", TEXT)

TEST = Table("test")
TEST.column(ID)
TEST.column(TEXT_COLUMN)
TEST.constraint(Unique(TEXT_COLUMN))


OTHER_ID = Column("other_id", INTEGER, NOT_NULL, References(TEST, on_delete=CASCADE))
TIMESTAMP = Column("timestamp", INTEGER, Default(CURRENT_UNIX_TIMESTAMP))

TEST2 = Table("test2")
TEST2.column(OTHER_ID)
TEST2.column(TIMESTAMP, version=2)


ADD_TEST = Insert().or_(REPLACE)\
    .table(TEST)\
    .columns(ID, TEXT_COLUMN)\
    .values(":id", ":text")\
    .build()

ADD_TEST2_FROM_TEST = Insert()\
    .table(TEST2)\
    .columns(OTHER_ID)\
    .select(
        Select()
        .fields(ID)
        .table(TEST)
        .where(Condition(ID, EQUAL, ":id"))
    )\
    .build()

DELETE_TEST = Delete()\
    .table(TEST)\
    .where(Condition(ID, EQUAL, ":id"))\
    .build()

GET_TEST_BY_ID_AND_TEXT = Select()\
    .fields(ID, TEXT_COLUMN)\
    .table(TEST)\
    .where(
        MultipleCondition(
            AND,
            Condition(ID, EQUAL, ":id"),
            Condition(TEXT_COLUMN, EQUAL, ":text"),
        )
    )\
    .build()

GET_ALL_TEST_SORTED_BY_TEXT = Select()\
    .fields(ID, TEXT_COLUMN)\
    .table(TEST)\
    .order_by(TEXT_COLUMN, ASC)\
    .build()

GET_ALL_TEST2_SORTED_BY_TIMESTAMP = Select()\
    .fields(OTHER_ID, TEXT_COLUMN, TIMESTAMP)\
    .table(TEST2).join(TEST, on=Condition(ID, EQUAL, OTHER_ID))\
    .order_by(Cast(TIMESTAMP, INTEGER), DESC)\
    .build()


class TestSqliteComponent(SqliteStorageComponent):
    def __init__(self):
        super().__init__(NAME, VERSION)
        self.managed_tables(TEST, TEST2)

    def save_test(self, test_id: int, text: str):
        self.statement(ADD_TEST).execute(id=test_id, text=text)

    def save_test2(self, test_id: int):
        # if user does not exists in test table, nothing will be inserted into test2
        self.statement(ADD_TEST2_FROM_TEST).execute(id=test_id)

    def delete_test(self, test_id: int):
        self.statement(DELETE_TEST).execute(id=test_id)

    def get_test(self, test_id: int, text: str):
        value = self.statement(GET_TEST_BY_ID_AND_TEXT).execute(id=test_id, text=text).first()
        if value is not None:
            value = value.map(self._test_to_dict)
        return value

    def get_all_test(self):
        return list(self.statement(GET_ALL_TEST_SORTED_BY_TEXT).execute().map(self._test_to_dict))

    def get_all_test2(self):
        return list(self.statement(GET_ALL_TEST2_SORTED_BY_TIMESTAMP).execute().map(self._test2_to_dict))

    @staticmethod
    def _test_to_dict(result: ResultRow):
        return {"id": result[ID], "text": result[TEXT_COLUMN]}

    @staticmethod
    def _test2_to_dict(result: ResultRow):
        return {"id": result[OTHER_ID], "text": result[TEXT_COLUMN], "timestamp": result[TIMESTAMP]}
