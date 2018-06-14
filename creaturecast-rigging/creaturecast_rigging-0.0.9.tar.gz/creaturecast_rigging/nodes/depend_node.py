import creaturecast_node.node as nod


class DependNode(nod.Node):

    default_data = dict(
        node_type=None,
        suffix='dep',
        side=0,
        index=0,
        size=1.0,
        icon='depend_node',
        base_type='depend_node'
    )

    auto_rename = False

    def __init__(self, *args, **kwargs):
        super(DependNode, self).__init__(*args, **kwargs)
        self.m_object = None

    def __str__(self):
        return str(self.data.get('name', '<%s>' % self.__class__.__name__))

    def __repr__(self):
        return self.__str__()
