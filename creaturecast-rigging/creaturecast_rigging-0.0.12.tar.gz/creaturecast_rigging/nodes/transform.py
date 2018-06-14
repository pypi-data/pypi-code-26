import creaturecast_rigging.nodes.dag_node as dag
import creaturecast_rigging.math.matrix as mtx


class Transform(dag.DagNode):

    default_data = dict(
        icon='transform',
        node_type='transform',
        suffix='gp',
        rotation_order=0,
        base_type='transform'
    )

    def __init__(self, *args, **kwargs):
        self.matrix = mtx.Matrix(*kwargs.pop('matrix', ()))
        super(Transform, self).__init__(*args, **kwargs)

    def get_translate(self):
        return self.matrix.get_translate()

    def set_translate(self, value):
        self.matrix.set_translate(value)
