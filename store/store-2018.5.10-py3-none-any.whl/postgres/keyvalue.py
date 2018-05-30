from pony.orm import db_session, select, desc

from store.postgres.postgres import PostgresStore


class KeyValueStore(PostgresStore):
    def __init__(self, data):
        data['unique'] = True
        super(KeyValueStore, self).__init__(data)
        key = data.get('key')
        self.key = str(key)

    def read(self, key=None):
        key = str(key) if key else self.key
        data = super(KeyValueStore, self).read(str(key))
        if data:
            return data['value']
        return None

    def delete(self, key=None):
        key = str(key) if key else self.key
        return super(KeyValueStore, self).delete(str(key))

    def set(self, key=None, value=None):
        key = str(key) if key else self.key
        if value is None:
            return self
        if self.read(key):
            self.update(key, value, mode='replace')
        else:
            self.create(key, value)
        return self

    def unset(self, key=None):
        key = str(key) if key else self.key
        self.delete(key)
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



