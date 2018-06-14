import creaturecast_rigging.nodes.joint as jnt
import creaturecast_rigging.rigging.transform_array as tay


class JointArray(tay.TransformArray):

    default_data = dict(
        icon='joint_array',
        node_type='transform',
        suffix='jay',
        item_data=dict(
            node_type='joint',
            )
        )
    node_constructor = jnt.Joint

    def __init__(self, *args, **kwargs):

        super(JointArray, self).__init__(*args, **kwargs)
