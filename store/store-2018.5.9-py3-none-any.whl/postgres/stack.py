from copy import copy

from pony.orm import db_session, select, desc

from store.postgres.postgres import PostgresStore


class StackStore(PostgresStore):
    def __init__(self, data):
        data['unique'] = True
        super(StackStore, self).__init__(data)
        key = data.get('key')
        self.key = str(key)

    def read(self, key=None):
        key = str(key) if key else self.key
        data = super(StackStore, self).read(str(key))
        if data:
            return data['value']
        return None

    def delete(self, key=None):
        key = str(key) if key else self.key
        return super(StackStore, self).delete(str(key))

    def __add__(self, that):
        if self.key:
            return self.push(value=that)
        return self

    def __sub__(self, that):
        if self.key:
            return self.remove(value=that, count=-1)
        return self

    def remove(self, key=None, value=None, count=0):
        key = str(key) if key else self.key
        elem = self.read(key)
        if elem:
            if count == 0:
                self.delete(str(key))
            elif count > 0:
                self._remove_value_count(elem, value, count)
                self.update(key, elem, mode='replace')
            elif count < 0:
                count = 0 - count
                elem.reverse()
                self._remove_value_count(elem, value, count)
                elem.reverse()
                self.update(key, elem, mode='replace')
        return self

    def _remove_value_count(self, data, value, count):
        for i in range(count):
            if value in data:
                data.remove(value)
            else:
                break

    def push(self, key=None, value=None):
        key = str(key) if key else self.key
        data = self.read(key)
        if data:
            data.append(value)
            self.update(str(key), data, mode='replace')
        else:
            self.create(str(key), [value])
        return self

    def pop(self, key=None):
        key = str(key) if key else self.key
        data = self.read(key)
        if data:
            if isinstance(data, list):
                last = data[-1]
                data = data[:-1]
                self.update(str(key), data, mode='replace')
                return last
            else:
                self.delete(str(key))
                return data
        else:
            return None

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
