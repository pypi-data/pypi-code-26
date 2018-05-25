from copy import copy

from pony.orm import Database, Required, db_session, select, desc, Json
from datetime import datetime

from store.base import BaseStore
from pony.orm import delete as db_delete


class PostgresStore(BaseStore):
    def __init__(self, data):
        db_type = data.get('type', 'postgres')
        db_user = data.get('user', 'dameng')
        db_password = data.get('password', 'hello')
        db_host = data.get('host', 'localhost')
        db_name = data.get('name', 'store')
        unique = data.get('unique', True)
        self.unique = unique

        self.db = Database(db_type, user=db_user, password=db_password, host=db_host, database=db_name)
        body = dict(__doc__='docstring',
                    create_at=Required(datetime, sql_default='CURRENT_TIMESTAMP', default=lambda: datetime.utcnow()),
                    update_at=Required(datetime, sql_default='CURRENT_TIMESTAMP', default=lambda: datetime.utcnow()),
                    key=Required(str, index=True, unique=unique),
                    value=Required(Json, volatile=True)
                    )

        table = data.get("table", "Store")
        if table[0].islower():
            table = table[0].upper() + table[1:]

        self.Store = type(table, (self.db.Entity,), body)
        self.db.generate_mapping(create_tables=True, check_tables=True)

    @db_session
    def create(self, key, value, id_=None):
        if self.unique:
            elem = select(e for e in self.Store if e.key == str(key)).order_by(lambda o: desc(o.create_at)).first()
            if elem is None:
                if id_:
                    self.Store(key=str(key), value=value, id=id_)
                else:
                    self.Store(key=str(key), value=value)
            else:
                elem.value = value
                elem.update_at = datetime.utcnow()
        else:
            if id_:
                self.Store(key=str(key), value=value, id=id_)
            else:
                self.Store(key=str(key), value=value)

    def _return_elem(self, elem):
        return {
            'id': copy(elem.id),
            'key': copy(elem.key),
            'value': copy(elem.value),
            'create_at': elem.create_at.strftime("%Y-%m-%d %H:%M:%S"),
            'update_at': elem.update_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @db_session
    def read(self, key):
        if isinstance(key, str):
            if self.unique:
                elem = select(e for e in self.Store if e.key == key).order_by(lambda o: desc(o.create_at)).first()
                if elem:
                    return self._return_elem(elem)
            else:
                elems = select(e for e in self.Store if e.key == key).order_by(lambda o: desc(o.create_at))[:]
                if elems:
                    return [self._return_elem(elem) for elem in elems]
        elif isinstance(key, int):
            elem = select(e for e in self.Store if e.id == key).order_by(lambda o: desc(o.create_at)).first()
            if elem:
                return self._return_elem(elem)
        return None

    def _update_elem(self, elem, value, mode='update'):
        if mode == 'update':
            value_db = copy(elem.value)
            if isinstance(value_db, str) and isinstance(value, str):
                elem.value = value
                elem.update_at = datetime.utcnow()
            elif isinstance(value_db, dict) and isinstance(value, dict):
                value_db.update(value)
                elem.value = value_db
                elem.update_at = datetime.utcnow()
            elif isinstance(value_db, list) and isinstance(value, list):
                vv = [v for v in value if v not in value_db]
                value_db.extend(vv)
                elem.value = value_db
                elem.update_at = datetime.utcnow()
            elif type(value_db) != type(value):
                elem.value = value
                elem.update_at = datetime.utcnow()
        elif mode == 'replace':
            elem.value = value
            elem.update_at = datetime.utcnow()
        elif mode == 'delete':
            value_db = copy(elem.value)
            if isinstance(value_db, dict):
                if isinstance(value, dict):
                    pop_keys = value.keys()
                    for k in pop_keys:
                        value_db.pop(k)
                elif isinstance(value, list):
                    for k in value:
                        value_db.pop(k)
                elem.value = value_db
                elem.update_at = datetime.utcnow()
            elif isinstance(value_db, list) and isinstance(value, list):
                updated_db = [e for e in value_db if e not in value]
                elem.value = updated_db
                elem.update_at = datetime.utcnow()

    @db_session
    def update(self, key, value, mode='update'):
        if isinstance(key, str):
            if self.unique:
                elem = select(e for e in self.Store if e.key == key).order_by(lambda o: desc(o.create_at)).first()
                if elem:
                    self._update_elem(elem, value, mode)
            else:
                elems = select(e for e in self.Store if e.key == key).order_by(lambda o: desc(o.create_at))[:]
                if elems:
                    for elem in elems:
                        self._update_elem(elem, value, mode)
        elif isinstance(key, int):
            elem = select(e for e in self.Store if e.id == key).order_by(lambda o: desc(o.create_at)).first()
            if elem:
                self._update_elem(elem, value, mode)

    @db_session
    def delete(self, key):
        if isinstance(key, str):
            db_delete(e for e in self.Store if e.key == key)
        elif isinstance(key, int):
            db_delete(e for e in self.Store if e.id == key)
