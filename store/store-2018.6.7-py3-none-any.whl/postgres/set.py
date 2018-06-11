from store.postgres.array import ArrayStore


class SetStore(ArrayStore):
    def __init__(self, data):
        data['unique'] = True
        super(SetStore, self).__init__(data)
        key = data.get('key')
        self.key = str(key)

    def __add__(self, that):
        if self.key:
            return self.add(value=that)
        return self

    def insert(self, key=None, value=None, index=0):
        raise Exception('forbidden')

    def add(self, key=None, value=None):
        key = str(key) if key else self.key
        elem = self.read(key)
        if elem and (value in elem):
            return self
        if elem:
            super(SetStore, self).insert(key=key, value=value, index=len(elem))
        else:
            super(SetStore, self).insert(key=key, value=value)
        return self

    def remove(self, key=None, value=None):
        key = str(key) if key else self.key
        elem = self.read(key)
        if (not elem) or (value not in elem):
            return
        super(SetStore, self).remove(key=key, value=value, count=1)

if __name__ == '__main__':
    a = SetStore({'table': 'test-set',
                  'name': 'test',
                  'user': 'dameng',
                  'password': 'hello',
                  'key': 'test'
                  })
    a.add('test', '3')
    a.add('test', '4')
    a.add('test', '3')
    d = a.read('test')
    print(d)
    a+'5'+'6'
    d = a.read('test')
    print(d)
