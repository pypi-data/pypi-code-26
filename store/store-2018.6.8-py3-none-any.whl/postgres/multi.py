from pony.orm import db_session, select, desc

from store.postgres.postgres import PostgresStore


class MultiStore(PostgresStore):
    def __init__(self, data):
        data['unique'] = False
        super(MultiStore, self).__init__(data)
        key = data.get('key')
        self.key = str(key)

    def read(self, key=None):
        key = str(key) if key else self.key
        data = super(MultiStore, self).read(str(key))
        if data:
            return [d['value'] for d in data]
        return None

    def delete(self, key=None, index=None):
        key = str(key) if key else self.key
        if index is None:
            return super(MultiStore, self).delete(str(key))
        elems = super(MultiStore, self).read(key)
        if isinstance(index, int):
            self._delete_elems_by_index(elems, index)
        elif isinstance(index, list):
            for i in index:
                self._delete_elems_by_index(elems, i)

    def _delete_elems_by_index(self, elems, index):
        try:
            del elems[index]
        except IndexError as e:
            pass
        else:
            ids = [e['id'] for e in elems]
            self._delete_by_ids(ids)

    @db_session
    def _delete_by_ids(self, ids):
        for id in ids:
            self.Store[id].delete()

    def __add__(self, that):
        if self.key:
            return self.add(value=that)
        return self

    def add(self, key=None, value=None):
        key = str(key) if key else self.key
        if value is None:
            return self
        self.create(key, value)
        return self


    @db_session
    def query(self, value):
        if value is None:
            return None
        elems = select(e for e in self.Store if value == e.value).order_by(lambda o: desc(o.create_at))[:]
        results = []
        for elem in elems:
            e = {
                'key': elem.key,
                'value': elem.value,
                'create_at': elem.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                'update_at': elem.update_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            results.append(e)
        return results



