from copy import copy
from datetime import datetime

from pony.orm import Database, Required, Json, db_session, select, commit, desc
from pony.orm import delete as db_delete

from store.base import BaseStore

from pony import options

options.CUT_TRACEBACK = False


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

    ######
    # for array

    @db_session
    def add(self, key, value):
        # value must be a list
        elem = select(e for e in self.Store if e.key == key).order_by(lambda o: desc(o.create_at)).first()
        if elem:
            value_db = copy(elem.value)
            if isinstance(value_db, list):
                if isinstance(value, str):
                    vs = [value] if value not in value_db else []
                else:
                    vs = [v for v in value if v not in value_db]
                value_db.extend(vs)
                elem.value = value_db
                elem.update_at = datetime.utcnow()
                commit()
            if key not in self.ids:
                self.ids.add(key)
        else:
            if isinstance(value, str):
                self.Store(key=key, value=[value])
            else:
                self.Store(key=key, value=value)
            if key not in self.ids:
                self.ids.add(key)
        elem = select(e for e in self.Store if e.key == key).order_by(lambda o: desc(o.create_at)).first()
        return {
            'key': copy(elem.key),
            'value': copy(elem.value),
            'create_at': elem.create_at.strftime("%Y-%m-%d %H:%M:%S"),
            'update_at': elem.update_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @db_session
    def remove(self, key, value):
        # value must be a list
        elem = select(e for e in self.Store if e.key == key).order_by(lambda o: desc(o.create_at)).first()
        if elem:
            value_db = copy(elem.value)
            if isinstance(value_db, list):
                if isinstance(value, str):
                    vs = [value] if value in value_db else []
                else:
                    vs = [v for v in value if v in value_db]
                for vv in vs:
                    value_db.remove(vv)
                elem.value = value_db
                elem.update_at = datetime.utcnow()
                commit()
        elem = select(e for e in self.Store if e.key == key).order_by(lambda o: desc(o.create_at)).first()
        return {
            'key': elem.key,
            'value': elem.value,
            'create_at': elem.create_at.strftime("%Y-%m-%d %H:%M:%S"),
            'update_at': elem.update_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @db_session
    def query(self, value, mode='should'):
        # value must be a list
        if value in (str, int, float, bool):
            value = [value]
        value = [v for v in value if v in (str, int, float, bool)]
        if len(value) == 0:
            return []
        if mode == 'must':
            elems = select(e for e in self.Store if value[0] in e.value).order_by(lambda o: desc(o.create_at))[:]
            if len(value) > 1:
                for i,v in enumerate(value[1:]):
                    for elem in elems:
                        if v not in elem.value:
                            del elems[i]
        else:
            elems = select(e for e in self.Store if value[0] in e.value).order_by(lambda o: desc(o.create_at))[:]
            if len(value) > 1:
                for i, v in enumerate(value[1:]):
                    es = select(e for e in self.Store if v in e.value).order_by(lambda o: desc(o.create_at))[:]
                    for e in es:
                        if e not in elems:
                            elems.append(e)

        results = []
        for elem in elems:
            e = {
                'key': copy(elem.key),
                'value': copy(elem.value),
                'create_at': elem.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                'update_at': elem.update_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            results.append(e)
        return results

    @db_session
    def queryd(self, value):
        # select from list, key must be matched, value is or relation
        keys = []
        values = []
        for k, v in value.items():
            if isinstance(v, str):
                keys.append(k)
                values.append(v)
            elif isinstance(v, list):
                for vv in v:
                    keys.append(k)
                    values.append(vv)

        elemss = []
        for i, k in enumerate(keys):
            elems = select(e for e in self.Store if k in e.value and values[i] in e.value[k]).order_by(
                lambda o: desc(o.create_at))[:]
            elemss.extend(elems)
        results = []
        for elem in elemss:
            e = {
                'key': elem.key,
                'value': elem.value,
                'create_at': elem.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                'update_at': elem.update_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            results.append(e)
        return results

    @db_session
    def reads(self, keys):
        results = []
        for key in keys:
            if self.unique:
                elem = select(e for e in self.Store if e.key == key).order_by(lambda o: desc(o.create_at)).first()
                if elem:
                    results.append({
                        'key': elem.key,
                        'value': elem.value,
                        'create_at': elem.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                        'update_at': elem.update_at.strftime("%Y-%m-%d %H:%M:%S"),
                    })
            else:
                elems = select(e for e in self.Store if e.key == key).order_by(lambda o: desc(o.create_at))[:]
                if elems:
                    for elem in elems:
                        results.append({
                            'key': elem.key,
                            'value': elem.value,
                            'create_at': elem.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                            'update_at': elem.update_at.strftime("%Y-%m-%d %H:%M:%S"),
                        })
        return results

    @db_session
    def read_prefix(self, key, pagenum=1, pagesize=20):
        elems = select(e for e in self.Store if e.key.startswith(key)).order_by(lambda o: desc(o.create_at)).page(
            pagenum=pagenum, pagesize=pagesize)
        results = []
        for elem in elems:
            results.append({
                'key': elem.key,
                'value': elem.value,
                'create_at': elem.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                'update_at': elem.update_at.strftime("%Y-%m-%d %H:%M:%S"),
            })
        return results

    @db_session
    def read_suffix(self, key, pagenum=1, pagesize=20):
        elems = select(e for e in self.Store if e.key.endswith(key)).order_by(lambda o: desc(o.create_at)).page(
            pagenum=pagenum, pagesize=pagesize)
        results = []
        for elem in elems:
            results.append({
                'key': elem.key,
                'value': elem.value,
                'create_at': elem.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                'update_at': elem.update_at.strftime("%Y-%m-%d %H:%M:%S"),
            })
        return results

    @db_session
    def read_in(self, key, pagenum=1, pagesize=20):
        elems = select(e for e in self.Store if key in e.key).order_by(lambda o: desc(o.create_at)).page(
            pagenum=pagenum, pagesize=pagesize)
        results = []
        for elem in elems:
            results.append({
                'key': elem.key,
                'value': elem.value,
                'create_at': elem.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                'update_at': elem.update_at.strftime("%Y-%m-%d %H:%M:%S"),
            })
        return results

    @db_session
    def read_all(self, pagenum=1, pagesize=20):
        elems = select(e for e in self.Store).order_by(lambda o: desc(o.create_at)).page(pagenum=pagenum,
                                                                                         pagesize=pagesize)
        results = []
        for elem in elems:
            results.append({
                'key': elem.key,
                'value': elem.value,
                'create_at': elem.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                'update_at': elem.update_at.strftime("%Y-%m-%d %H:%M:%S"),
            })
        return results



if __name__ == '__main__':
    # s = PostgresStore({"table": "hello_world"})
    # s.create('1', {1: 3})
    # s.create('2', {'hello': 'world'})
    # s.create('3', {'hello': {1: 'world', 2: '世界'}})
    # s.create('4', {'t': ["你好", "世界", "测试"]})
    # s.create('5', {'t': ["世界", "你好", "改动"]})
    # s.create('6', {'t': ["刺激", "1995", "改动一下"]})
    # s.create('7', {'t': ["明天", "幸福"]})
    # s.create('8', {'t2': ["明天", "幸福"]})
    # s.create('9', {'t3': ["明天", "幸福"]})
    # s.create('10', {'测试': ["明天", "幸福"]})
    # s.create('11', ['测试'])
    # # r = s.query('hello')
    # r = s.queryd({'t': ["世界", "1995"]})
    # print(r)
    # r = s.queryd({'t': ["幸福"]})
    # print(r)
    # r = s.query(["测试"])
    # r = s.query("测试")
    # print(r)
    # print('.' * 80)
    # s.add('12', "t1")
    # s.add('12', ["t1"])
    # s.add('12', ["t1", "t2", "t3", "t4"])
    # s.remove('12', "t1")
    # s.remove('12', ["t2", "t4"])
    # print('.' * 80)
    # s.create('http://127.0.0.1', ['测试'])
    # s.create('https://127.0.0.1', ['测试'])
    # r = s.read_prefix('https')
    # print(r)
    # r = s.read_in('')
    # print(r)
    # r = s.reads(['1', '2'])
    # print(r)
    # for a in r:
    #     print(a)
    # r = s.query('hello')

    # r = s.query({'hello': 'world'})
    # print(r)
    # r = s.query({'hello':{1:'world', 2: '世界'}})
    # print(r)
    # s.delete('1')
    # with open('test.txt', 'r') as f:
    #     content = f.read()
    # r = s.create('hello.txt', 'test.txt', mode='file')
    # print(s.read(r))
    s = PostgresStore({"table": "hello_world", "unique": False})
    # m = s.create("t1", {"t1": "t2"})
    m = s.read(2)
    print(m)
