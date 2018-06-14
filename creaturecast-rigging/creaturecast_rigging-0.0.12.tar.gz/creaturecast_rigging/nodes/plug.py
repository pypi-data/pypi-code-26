import PySignal as sig
import copy


class Plug(object):

    default_data = dict(
        create=False,
        name='FUCK',
        value=None
    )

    data_changed = sig.ClassSignal()

    def __init__(self, *args, **kwargs):

        super(Plug, self).__init__()
        if not isinstance(kwargs.get('name', None), basestring):
            raise Exception('Plug name invalid : "%s"' % kwargs.get('name', None))

        self.node = args[0]
        self.data = copy.copy(self.default_data)
        self.data.update(kwargs)
        self.incoming = None
        self.outgoing = []

    def __str__(self):
        return str(self.data['name'])

    def __repr__(self):
        return self.__str__()

    @property
    def value(self):
        return self.data.get('value', None)

    @value.setter
    def value(self, value):
        self.data['value'] = value
        self.data_changed.emit(value)

    def set_value(self, value):
        self.value = value

    def connect_to(self, *args):
        for plug in args:
            self.outgoing.append(plug)
            plug.incoming = self
            self.data_changed.connect(plug.set_value)
            self.data_changed.emit(self.value)
