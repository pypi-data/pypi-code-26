import uuid
import copy
import creaturecast_rigging.controller as hdr


class Attribute(object):

    default_data = dict(
        icon='attribute',
        name='attribute',
        value=None,
        type=None,
        default_value=None
    )

    def __init__(self, owner, **kwargs):
        super(Attribute, self).__init__()
        self.owner = owner
        self.parent = None
        self.children = []
        self.outgoing_connections = []
        self.incoming_connections = []
        self.data = copy.copy(self.default_data)
        self.data.update(kwargs)
        self.controller = kwargs.pop('controller', self.default_controller)
        self.create()

    def __str__(self):
        return '<%s %s.%s>' % (self.__class__.__name__, self.owner.data['name'], self.data['name'])

    def __repr__(self):
        return self.__str__()

    def create(self):
        self.parent = self.data.pop('parent', None)
        if self.parent:
            self.parent.children.append(self)
        self.data['uuid'] = str(uuid.uuid4())
        self.data['class'] = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        if self.data['default_value'] and not self.data['value']:
            self.data['value'] = self.data['default_value']
        elif self.data['value'] and not self.data['default_value']:
            self.data['default_value'] = self.data['value']
        self.controller.create.emit(self)

    def destroy(self):
        for attribute in self.outgoing_connections:
            self.disconnect(attribute)
        for attribute in self.incoming_connections:
            attribute.disconnect(self)
        self.controller.delete.emit(self)

    def connect(self, attribute, **kwargs):
        if attribute in self.outgoing_connections:
            raise Exception('%s is already connected to %s' % (self, attribute))
        if not self.data['type'] == attribute.data['type']:
            raise Exception('%s is not the same type as %s and can not be connected' % (self, attribute))

        self.outgoing_connections.append(attribute)
        attribute.incoming_connections.append(self)
        self.controller.connect.emit(self, attribute, **kwargs)

    def disconnect(self, attribute, **kwargs):
        if attribute not in self.outgoing_connections:
            raise Exception('%s is not connected to %s' % (self, attribute))
        self.outgoing_connections.remove(attribute)
        attribute.incoming_connections.remove(self)
        self.controller.disconnect.emit(self, attribute, **kwargs)

    def get_value(self):
        return self.data['value']

    def set_value(self, value):
        self.data['value'] = value
        for attribute in self.outgoing_connections:
            attribute.set_value(value)
        self.controller.value_changed.emit(self)

    def get_type(self):
        return type(self.data['value'])
