from pony.orm import db_session, select, desc

from store.postgres.postgres import PostgresStore


class DictionaryStore(PostgresStore):
    def __init__(self, data):
        data['unique'] = True
        super(DictionaryStore, self).__init__(data)
        key = data.get('key')
        self.key = str(key)

    def read(self, key=None):
        key = str(key) if key else self.key
        data = super(DictionaryStore, self).read(str(key))
        if data:
            return data['value']
        return None

    def delete(self, key=None):
        key = str(key) if key else self.key
        return super(DictionaryStore, self).delete(str(key))

    def __add__(self, that):
        if self.key:
            return self.add(value=that)
        return self

    def __sub__(self, that):
        if self.key:
            return self.remove(value=that, count=1)
        return self

    def add(self, key=None, value=None):
        key = str(key) if key else self.key
        if value is None:
            return self
        if isinstance(value, dict):
            elem = self.read(key)
            if elem:
                elem.update(value)
                self.update(key, elem, mode='replace')
            else:
                self.create(key, value)
        else:
            value = {'_': value}
            return self.add(key, value)


    def remove(self, key=None, value=None):
        key = str(key) if key else self.key
        if value is None:
            return self.delete(key)
        elem = self.read(key)
        if isinstance(value, list):
            for v in value:
                if v in elem.keys():
                    elem.pop(v, None)
        elif isinstance(value, dict):
            for k,v in value:
                if k in elem.keys():
                    elem_value = elem[k]
                    if isinstance(elem_value, list):
                        if v in elem[k]:
                            elem[k].remove(v)
                    else:
                        if v == elem[k]:
                            elem.pop(k, None)
        else:
            if value in elem.keys():
                elem.pop(value, None)

        self.update(key, elem, mode='replace')



    @db_session
    def query(self, value):
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


