import time

from sqlite_framework.log.impl import BasicSqliteLogger
from sqlite_framework.session.session import SqliteSession
from sqlite_framework_test.factory import TestSqliteStorageComponentFactory


session = SqliteSession(":memory:", debug=True, enable_foreign_keys=True)

with session:
    session.init()
    component_factory = TestSqliteStorageComponentFactory(session, BasicSqliteLogger())
    test_component = component_factory.test()

with session:
    test_component.save_test(1, "test 1")
    test_component.save_test(2, "test 2")
    test_component.save_test(55, "test 55")
    test_component.save_test2(55)
    time.sleep(1.1)
    test_component.save_test2(2)
    time.sleep(1.1)
    test_component.save_test2(55)

print(test_component.get_test(1, "test 1"))
print(test_component.get_test(2, "test 4"))
print(test_component.get_all_test())
print(test_component.get_all_test2())

with session:
    test_component.delete_test(55)

print(test_component.get_all_test())
print(test_component.get_all_test2())
