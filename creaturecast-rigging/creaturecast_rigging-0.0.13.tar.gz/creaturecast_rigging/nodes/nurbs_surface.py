import creaturecast_rigging.nodes.dag_node as dag


class NurbsSurface(dag.DagNode):

    default_data = dict(
        icon='nurbs_plane',
        node_type='nurbsSurface',
        base_type='nurbs_surface',
        suffix='nsf'
    )

    def __init__(self, *args, **kwargs):
        super(NurbsSurface, self).__init__(*args, **kwargs)