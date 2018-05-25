from copy import copy

from pony.orm import db_session, select, desc

from store.postgres.postgres import PostgresStore


class ArrayMultiStore(PostgresStore):
    def __init__(self, data):
        data['unique'] = False
        super(ArrayMultiStore, self).__init__(data)
        key = data.get('key')
        self.key = str(key)

    def read(self, key=None):
        key = str(key) if key else self.key
        data = super(ArrayMultiStore, self).read(str(key))
        if data:
            return [d['value'] for d in data]
        return None

    def delete(self, key=None):
        key = str(key) if key else self.key
        return super(ArrayMultiStore, self).delete(str(key))

    def __add__(self, that):
        if self.key:
            return self.insert(value=that, index=len(self))
        return self

    def __sub__(self, that):
        if self.key:
            return self.remove(value=that, count=1)
        return self

    def __len__(self):
        elems = self.read()
        if elems and isinstance(elems, list):
            return len(elems)
        return 0

    def remove(self, key=None, value=None, count=0, index=0):
        key = str(key) if key else self.key
        elem = self.read(key)
        if elem and isinstance(elem, list):
            if len(elem) == 0:
                self.delete(key)
            else:
                if value is None:
                    if isinstance(index, int):
                        elem = self._remove_by_index(elem, index)
                    elif isinstance(index, list):
                        for i in index:
                            if isinstance(index, int):
                                elem = self._remove_by_index(elem, index)
                else:
                    self._remove_by_value(key, elem, value, count)
                self.update(key, elem, mode='replace')
        return self

    def _remove_value_count(self, data, value, count):
        for i in range(count):
            if value in data:
                data.remove(value)
            else:
                break

    def _remove_by_value(self, key, elem, value, count):
        if count == 0:
            self.delete(key)
        elif count > 0:
            self._remove_value_count(elem, value, count)
            self.update(key, elem, mode='replace')
        elif count < 0:
            count = 0 - count
            elem.reverse()
            self._remove_value_count(elem, value, count)
            elem.reverse()
            self.update(key, elem, mode='replace')

    def _remove_by_index(self, elem, index):
        try:
            index_data = elem[index]
        except IndexError as e:
            pass
        else:
            del elem[index]
        return elem

    def insert(self, key=None, value=None, index=0):
        key = str(key) if key else self.key
        elem = self.read(key)
        if elem:
            elem.insert(index, value)
            self.update(key, elem, mode='replace')
        else:
            self.create(key, [value])
        return self




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
