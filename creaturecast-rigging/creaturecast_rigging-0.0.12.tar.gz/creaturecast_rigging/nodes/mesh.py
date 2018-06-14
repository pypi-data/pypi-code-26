import creaturecast_rigging.nodes.dag_node as dag


class Mesh(dag.DagNode):

    default_data = dict(
        icon='polygon',
        node_type='mesh',
        suffix='msh',
        base_type='mesh'
    )

    def __init__(self, *args, **kwargs):
        super(Mesh, self).__init__(*args, **kwargs)

        self.shader = None

