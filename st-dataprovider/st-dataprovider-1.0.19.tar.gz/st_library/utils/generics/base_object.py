import collections


class BaseModel(collections.Mapping):
    def get_initial_data(self):
        raise NotImplementedError

    def __init__(self):
        self._data = None
        self._data = self.get_initial_data()

    def __getitem__(self, key):
        return self._data[key]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)
