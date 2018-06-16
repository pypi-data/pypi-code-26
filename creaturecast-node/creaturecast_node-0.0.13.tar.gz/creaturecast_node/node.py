import os
import json
import copy
import uuid
import itertools
import PySignal
print __file__.replace('\\', '/')
print os.path.dirname(__file__.replace('\\', '/'))
print '%s/data/rig_settings.json' % os.path.dirname()
print '---------->>'

rig_settings_path = '%s/data/rig_settings.json' % os.path.dirname(__file__.replace('\\', '/'))
with open(rig_settings_path, mode='r') as f:
    rig_settings = json.load(f)

handle_shapes_path = '%s/data/handle_shapes.json' % os.path.dirname(__file__.replace('\\', '/'))
with open(handle_shapes_path, mode='r') as f:
    handle_shapes = json.load(f)


class Node(object):
    """
    An abstract data container
    Can be organized hierarchically
    """

    inherited_data = ['size', 'root_name', 'side', 'index']
    invalid_keyword_args = []

    default_data = dict(
        size=1.0,
        side=2,
        root_name='node',
        created=False,
        layer='node',
        base_type='node'
    )

    def __init__(self, *args, **kwargs):
        super(Node, self).__init__()


        parent = kwargs.pop('parent', None)
        database_object = kwargs.pop('database_object', None)
        self.factory = kwargs.pop('factory', BaseNodeFactory())

        #Remove invalid kwargs
        for arg in self.invalid_keyword_args:
            kwargs.pop(arg, None)

        #if first arg is a node, extract data and update kwargs
        if args and isinstance(args[0], Node):
            data = args[0].data
            data.update(kwargs)
            kwargs = data

        self.object_handle = None
        self.parent = None
        self.children = []

        for key in self.inherited_data:
            if key not in kwargs and parent and key in parent.data:
                kwargs[key] = parent.data[key]

        data = extract_default_data(self.__class__)
        data.update(kwargs)
        data['uuid'] = data.get('uuid', str(uuid.uuid4()))
        if 'class_type' not in data:
            data['class_type'] = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        self.data = JsonDict(serializable_check=True, **data)
        if parent:
            self.set_parent(parent)
        self.data['name'] = self.factory.create_name_string(**self.data)

        self.plug_dictionary = dict()
        self.plugs = Plugs(self)
        self.nodes = Nodes(self)

    def __copy__(self):
        raise Exception('%s\'s are not copyable' % self.__class__.__name__)

    def __eq__(self, other):
        if other.__class__ == self.__class__:
            if self.data['uuid'] == other.data['uuid']:
                return True
        return False

    def __str__(self):
        if self.data.get('name', None):
            return '<%s "%s">' % (self.__class__.__name__, self.data['name'])
        return '<%s>' % self.__class__.__name__

    def __repr__(self):
        return self.__str__()

    def __delete__(self):
        self.factory.nodes.pop(self.data['uuid'])
        self.unparent()
        #self.factory.names.remove(self.data['name'])
        #self.factory.deleted.emit(self)
        #for child in self.children:
        #    child.__delete__()

    def select(self):
        self.factory.selected_nodes(self)

    def create_plug(self, name, **kwargs):
        kwargs['name'] = name
        plug = Plug(self, **kwargs)
        plug.data['create'] = True
        return plug

    def parent_callback(self, child):
        self.children.append(child)

    def set_parent(self, parent):
        """
        Hooks into callbacks related to setting parents
        """
        #if self == parent:
        #    self.factory.error.emit('Cannot parent %s to itself' % self.data['name'])
        #elif parent in self.get_descendants():
        #    self.factory.error.emit('Cannot parent %s to one of its children' % self.data['name'])
        #    self.unparent()
        if not parent:
            raise Exception('Cant set parent to None')
        self.factory = parent.factory

        if self.data['uuid'] in self.factory.nodes:
            raise Exception('Factory already has the node %s, %s' % (self, self.data['uuid']))

        self.factory.start_parent.emit(self, parent)
        self.parent = parent
        parent.parent_callback(self)
        self.factory.end_parent.emit(self, parent)


    def unparent(self):
        """
        Hooks into callbacks related to un-parenting nodes
        """
        if self.parent:
            self.factory.start_unparent.emit(self)
            if self.parent:
                self.parent.children.remove(self)
            self.parent = None
            if self in self.factory.selected_nodes:
                self.factory.selected_nodes.remove(self)
                self.factory.selection_changed.emit(self.factory.selected_nodes)
            self.factory.end_unparent.emit(self)

    def delete(self):
        self.__delete__()

    def get_descendants(self, node_type=None):
        descendants = []
        for child in self.get_children(node_type=node_type):
            descendants.append(child)
            descendants.extend(child.get_descendants(node_type=node_type))
        return descendants

    def get_children(self, node_type=None):
        if node_type is None:
            return self.children
        return [x for x in self.children if isinstance(x, node_type)]

    def insert_child(self, index, child):
        child.unparent()
        if child:
            child.parent = self
            self.children.insert(index, self)

    def get_index(self):
        if self.parent and self in self.parent.children:
            return self.parent.children.index(self)
        return 0

    def get_long_name(self):
        nodes = self.get_descendants()
        nodes.append(self)
        return '|%s' % ('|'.join(nodes))

    def get_index_name(self):
        return self.factory.get_index_name(**self.data)

    def create_child(self, **kwargs):
        kwargs['parent'] = self
        return self.__class__(**kwargs)

    def get_short_name(self):
        return self.factory.get_short_name(**self.data)

    def create(self):

        #if self.data['created']:
        #    raise Exception('%s has already been created.' % self)

        self.factory.created.emit(self)
        self.data['created'] = True
        return self


class Nodes(dict):

    def __init__(self, node):
        super(Nodes, self).__init__()
        self.node = node

    def __getitem__(self, key):
        return super(Nodes, self).__getitem__(key)


    def __setitem__(self, key, value):
        return super(Nodes, self).__setitem__(key, value)

    def get(self, *args, **kwargs):
        return super(Nodes, self).get(*args, **kwargs)


        '''
        recursive = kwargs.get('recursive', False)
        instance_type = kwargs.get('instance_type', None)
        if kwargs.get('recursive', False):
            nodes = [get_node(x) for x in super(Nodes, self).get(*args)]
            if instance_type:
                nodes = [x for x in nodes if isinstance(x, instance_type)]
            child_nodes = []
            for node in nodes:
                if args[0] in node.nodes:
                    child_nodes.extend(node.nodes.get(
                        recursive=recursive,
                        instance_type=instance_type,
                        *args
                    ))
            nodes.extend(child_nodes)
            return nodes
        else:
            return [get_node(x) for x in super(Nodes, self).get(*args)]
        '''

class Plugs(object):
    def __init__(self, owner):
        super(Plugs, self).__init__()
        self.owner = owner
        self.current = 0

    def __getitem__(self, key):
        if key in self.owner.plug_dictionary:
            return self.owner.plug_dictionary[key]
        plug = Plug(self.owner, name=key)
        self.owner.plug_dictionary[key] = plug
        return plug

    def set_values(self, **kwargs):
        for key in kwargs:
            self[key].set_value(kwargs[key])


class Plug(object):

    default_data = dict(
        create=False,
        name='PLUG',
        value=None
    )

    def __init__(self, *args, **kwargs):

        super(Plug, self).__init__()
        name = kwargs.get('name', None)
        if not isinstance(name, basestring):
            raise Exception('Plug name invalid : "%s"' % name)

        kwargs['uuid'] = kwargs.get('uuid', str(uuid.uuid4()))

        self.node = args[0]
        self.data = copy.copy(self.default_data)
        self.data.update(kwargs)
        self.incoming = None
        self.outgoing = []
        self.node.plug_dictionary[name] = self

    def __str__(self):
        return '%s.%s' % (self.node, self.data['name'])

    def __repr__(self):
        return self.__str__()

    @property
    def value(self):
        return self.data.get('value', None)

    @value.setter
    def value(self, value):
        self.data['value'] = value

    def set_value(self, value):
        self.value = value

    def connect_to(self, *args):
        for plug in args:
            if plug in self.outgoing:
                raise Exception('%s is already conected to %s' % (self, plug))
            self.outgoing.append(plug)
            plug.incoming = self


class JsonDict(dict):
    """
    A Dictionary-Like object that checks that data is json serializable
    """

    def __init__(self, serializable_check=True, *args, **kwargs):
        super(JsonDict, self).__init__(*args, **kwargs)
        self.serializable_check = serializable_check

    def __setitem__(self, key, value):
        if self.serializable_check:
            try:
                json.dumps(value)
            except TypeError, e:
                raise TypeError('Unable to serialize value.%s' % e.message)
        super(JsonDict, self).__setitem__(key, value)


def extract_default_data(class_object):
    data = dict()
    if hasattr(class_object, 'default_data'):
        data = copy.copy(class_object.default_data)
    for base_class in class_object.__bases__:
        base_data = extract_default_data(base_class)
        base_data.update(data)
        data = base_data
    return data


def create_alpha_dictionary(depth=4):
    ad = {}
    mit = 0
    for its in range(depth)[1:]:
        for combo in itertools.product('abcdefghijklmnopqrstuvwxyz', repeat=its):
            ad[mit] = ''.join(combo)
            mit += 1
    return ad


alpha_dictionary = create_alpha_dictionary()


class BaseNodeFactory(object):

    created = PySignal.ClassSignal()
    start_parent = PySignal.ClassSignal()
    end_parent = PySignal.ClassSignal()
    start_unparent = PySignal.ClassSignal()
    end_unparent = PySignal.ClassSignal()
    end_create = PySignal.ClassSignal()
    deleted = PySignal.ClassSignal()
    selection_changed = PySignal.ClassSignal()
    error = PySignal.ClassSignal()
    root_about_to_change = PySignal.ClassSignal()
    root_changed = PySignal.ClassSignal()
    data_changed = PySignal.ClassSignal()

    def __init__(self, *args, **kwargs):
        super(BaseNodeFactory, self).__init__()
        self.names = []
        self.nodes = dict()
        self.selected_nodes = []
        self.root = None

    def select_nodes(self, *nodes):
        nodes = flatten_nodes(*nodes)
        for node in nodes:
            if node.data['uuid'] not in self.nodes:
                raise Exception('The node cannot be selected "%s"' % node)
        self.selected_nodes = list(nodes)
        self.selection_changed.emit(self.selected_nodes)

    def set_root(self, root):
        self.root_about_to_change.emit()
        self.root = root
        self.names = [root.data['name']]
        self.nodes = {root.data['uuid']: root}
        root.factory = self
        for descendant in root.get_descendants():
            descendant.factory = self
            self.names.append(descendant.data['name'])
            self.nodes[descendant.data['uuid']] = descendant
        self.root_changed.emit(root)

    def create_name_string(self, **kwargs):
        existing_name = kwargs.get('name', None)
        if existing_name:
            self.names.append(existing_name)
            return existing_name
        side = kwargs.get('side', None)
        index = kwargs.get('index', None)
        side_prefix = ''
        index_string = ''
        suffix = kwargs.get('suffix', None)
        root_name = kwargs.get('root_name', '')
        suffix_string = ''
        if suffix:
            suffix_string = '_%s' % suffix
        if side is not None:
            side_prefix = '%s_' % rig_settings['side_prefixes'][side]
        if index is not None:
            index_string = '_%s' % alpha_dictionary[index]
        name = '%s%s%s%s' % (
            side_prefix,
            root_name,
            index_string,
            suffix_string
        )
        if existing_name in self.names:
            self.names.remove(existing_name)
        self.names.append(name)
        return name

    def get_index_name(self, **kwargs):
        index = kwargs.get('index', None)
        index_string = ''
        root_name = kwargs.get('root_name')
        if index is not None:
            index_string = '_%s' % alpha_dictionary[index]
        index_name = '%s%s' % (
            root_name,
            index_string
        )
        return index_name


    def get_uuid(self, item):
        if isinstance(item, Node):
            return item.data['uuid']
        elif isinstance(item, basestring):
            return item
        else:
            raise Exception('Node type invalid %s %s' % (item, type(item)))

    def get_node(self, item):
        if isinstance(item, Node):
            return item
        elif isinstance(item, basestring):
            #if item in self.nodes:
            return self.nodes[item]
        else:
            raise Exception('Node type invalid %s %s' % (item, type(item)))



def flatten_nodes(*args):
    flattened_args = []
    for arg in args:
        if isinstance(arg, (list, tuple, set)):
            flattened_args.extend(flatten_nodes(*[x for x in arg]))
        elif isinstance(arg, dict):
            flattened_args.extend(flatten_nodes(*arg.values()))
        else:
            flattened_args.append(arg)
    return flattened_args


default_factory = BaseNodeFactory()
