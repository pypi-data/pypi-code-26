import creaturecast_rigging.nodes.dag_node as dag


class Locator(dag.DagNode):

    default_data = dict(
        icon='locator',
        node_type='locator',
        suffix='loc'
    )

    def __init__(self, *args, **kwargs):
        super(Locator, self).__init__(*args, **kwargs)
