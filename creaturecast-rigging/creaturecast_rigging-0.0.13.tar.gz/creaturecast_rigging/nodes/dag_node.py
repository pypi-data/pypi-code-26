import creaturecast_rigging.nodes.depend_node as dep


class DagNode(dep.DependNode):

    default_data = dict(
        suffix='dag',
        icon='depend_node',
        base_type='dag_node'
    )

    def __init__(self, *args, **kwargs):

        #dag_parent = kwargs.get('dag_parent', None)
        #parent = kwargs.get('parent', None)

        super(DagNode, self).__init__(*args, **kwargs)

        #self.dag_parents = set()
        #self.dag_children = set()

        #if dag_parent:
        #    self.set_dag_parent(dag_parent)
        #elif isinstance(parent, DagNode):
        #    self.set_dag_parent(parent)
        self.shader = None
        #self.create_plug(name='visibility', value=True)

    def remove_dag_parent(self):
        for parent in self.dag_parents:
            parent.dag_children.remove(self)
        self.dag_parents = set()

    def set_dag_parent(self, *args):
        self.remove_dag_parent()
        self.dag_parents = set(args)
        for parent in args:
            parent.dag_children.add(self)
