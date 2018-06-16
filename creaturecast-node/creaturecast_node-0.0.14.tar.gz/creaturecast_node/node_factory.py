import os
import json
import copy
import itertools
import pprint
import PySignal
import creaturecast_node.node as nod
import uuid


class NodeFactory(nod.BaseNodeFactory):

    root_changed = PySignal.ClassSignal()

    def __init__(self, *args, **kwargs):
        super(NodeFactory, self).__init__(*args, **kwargs)


def deserialize_nodes(kwargs_list):

    if isinstance(kwargs_list, basestring):
        try:
            kwargs_list = json.loads(kwargs_list)
        except:
            raise Exception('Unable to parse json string.')

    temporary_factory = nod.BaseNodeFactory()

    connections = dict()
    plugs = dict()
    new_nodes = []

    for kwargs in kwargs_list:
        uuid = kwargs['uuid']

        #I think this is to allow parenting to existing nodes
        #It may however be inesicerry
        #Temp Factory Check
        if not uuid in temporary_factory.nodes:
            connections[uuid] = kwargs.pop('nodes')
            plugs[uuid] = kwargs.pop('plugs')
            new_node = deserialize_node(kwargs, temporary_factory)
            new_nodes.append(new_node)
        else:
            new_nodes.append(temporary_factory.nodes[uuid])

    connect_nodes(connections, temporary_factory)
    deserialize_plugs(plugs, temporary_factory)
    change_uuids(*new_nodes)
    #Shaders should be build elseware

    return new_nodes

def change_uuids(*nodes):
    for node in nodes:
        node.data['uuid'] = str(uuid.uuid4())
        for key in node.plug_dictionary:
            node.plug_dictionary[key].data['uuid'] = str(uuid.uuid4())


def connect_nodes(connections, factory):
    for uuid in connections:
        connect_node(
            factory.nodes[uuid],
            connections[uuid],
            factory
        )


def connect_node(node, connections, factory):
        for key in connections:
            get_item = connections[key]
            if isinstance(get_item, (list, tuple, set)):
                connected_nodes = []
                for x in get_item:
                    if x in factory.nodes:
                        connected_nodes.append(factory.nodes[x])
                node.nodes[key] = connected_nodes
            else:
                if get_item in factory.nodes:
                    node.nodes[key] = factory.nodes[get_item]


def deserialize_node(data, factory):

    parent = data.get('parent', None)
    if parent:
        data['parent'] = factory.nodes[parent]
    else:
        data['factory'] = factory
    new_node = deserialize_instance(**data)
    factory.nodes[data['uuid']] = new_node
    return new_node


def select_nodes(self, *nodes):
    self.selected_nodes = nodes
    self.selection_changed.emit(self.selected_nodes)


def serialize(node):
    data = [serialize_node(node)]
    for child in node.children:
        data.extend(serialize(child))
    return data


def serialize_node(node):
    node_data = dict(node.data)
    if node.parent:
        node_data['parent'] = node.parent.data['uuid']
    node_data['nodes'] = serialize_node_connections(node)
    node_data['plugs'] = serialize_plugs(node)
    if node.data['base_type'] == 'part_template':
        handles = node.nodes.get('handles', [])
        if handles:
            node_data['matrices'] = [x.matrix.values for x in handles]
        else:
            node_data['matrices'] = [x.values for x in node.matrices]
    if node.data['base_type'] == 'transform':
        node_data['matrix'] = node.matrix.values

    return dict(node_data)


def serialize_rig(root):
    root_data = serialize_node(root)
    root_data['edit_mode'] = True
    data = [root_data]
    for rig in root.children:
        rig_data = serialize_node(rig)
        data.append(rig_data)
        for part in rig.nodes.get('parts', []):
            part_data = serialize_node(part)
            data.append(part_data)
    return data


def deserialize_instance(**kwargs):
    class_tokens = kwargs['class_type'].split('.')
    try:
        module = __import__('.'.join(class_tokens[0:-1]), fromlist=['.'])
        new_node = module.__dict__[class_tokens[-1]](**kwargs)
    except:
        new_node = nod.Node(**kwargs)
    return new_node


def serialize_node_connections(node):
    node_connections = dict()
    for key in node.nodes:
        value = node.nodes[key]
        if isinstance(value, (list, tuple, set)):
            node_connections[key] = [x.data['uuid'] for x in value]
        elif isinstance(value, nod.Node):
            node_connections[key] = value.data['uuid']
        else:
            raise Exception('connected node is invalid %s.%s = type(%s)' % (node.data['root_name'], key, type(value)))
    return node_connections


def serialize_plugs(node):

    plug_data = nod.JsonDict()
    for key in node.plug_dictionary:
        plug = node.plug_dictionary[key]
        plug_data[key] = dict(plug.data)
        if not isinstance(plug.data['name'], basestring):
            raise Exception('invalid Plug Name %s.%s' % (node, plug.data['name']))
        connections = []
        for x in plug.outgoing:
            connections.append(x.data['uuid'])
        plug_data[key]['connections'] = connections
    return dict(plug_data)


def deserialize_plugs(plugs_dict, factory):
    connections = dict()
    for x in plugs_dict:
        node = factory.nodes[x]
        plugs = plugs_dict[x]
        for y in plugs:
            plug_data = plugs[y]
            uuid = plug_data['uuid']
            connections[uuid] = plug_data.pop('connections')
            plug = nod.Plug(node, **plug_data)
            factory.nodes[uuid] = plug

    for key in connections:
        for x in connections[key]:
            source = factory.nodes[key]
            destination = factory.nodes[x]
            source.connect_to(destination)

