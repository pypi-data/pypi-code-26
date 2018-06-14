import creaturecast_rigging.nodes.transform as trn


class Skeleton(trn.Transform):

    default_data = dict(
        icon='joint_array',
        node_type='transform',
        suffix='skel'
    )

    def __init__(self, *args, **kwargs):
        super(Skeleton, self).__init__(*args, **kwargs)

