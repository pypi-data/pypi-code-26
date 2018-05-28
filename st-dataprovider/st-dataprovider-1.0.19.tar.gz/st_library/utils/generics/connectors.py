from collections import OrderedDict

from st_library.exceptions import DatabaseConnectionError, DatabaseNotFound
from st_library.core.metadata.metadata import _METADATA


class ConnectorContainer(object):
    def __init__(self, *args, **kwargs):
        self._data_initialized = False
        self._list = list()
        self._dict = OrderedDict()

    def __getitem__(self, item):
        if isinstance(item, int):
            try:
                result = self._list[item]
            except IndexError:
                if self._data_initialized:
                    raise DatabaseNotFound('The database with index {} not found'.format(item))
                else:
                    self._initialize_data()
                    result = self._list[item]

            return result

        if isinstance(item, str):
            try:
                result = self._dict[item]
            except KeyError:
                if self._data_initialized:
                    raise DatabaseNotFound('The database with name "{}" not found'.format(item))
                else:
                    self._initialize_data()
                    result = self._dict[item]

            return result

        raise ValueError('Invalid key')

    def _initialize_data(self):
        try:
            self._do_initialize_data()
        except Exception as e:
            raise DatabaseConnectionError(str(e))

        self._data_initialized = True

    def _do_initialize_data(self):
        raise NotImplementedError

    @property
    def names(self):
        if not self._data_initialized:
            self._initialize_data()
        return list(self._dict.keys())

    def __repr__(self):
        names = self.names
        return repr(self._list)

    @property
    def default(self):
        names = self.names
        return self._list[0]

    def _fetch_param_dict(self, param_ids):
        param_dict = dict()
        for param_id in param_ids:
            param_dict[param_id] = _METADATA.get_parameter_value(param_id)
        return param_dict
