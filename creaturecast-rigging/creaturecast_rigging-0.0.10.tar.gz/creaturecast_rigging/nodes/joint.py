import creaturecast_rigging.nodes.transform as trn


class Joint(trn.Transform):

    default_data = dict(
        icon='joint',
        node_type='joint',
        suffix='jnt'
    )

    def __init__(self, *args, **kwargs):
        super(Joint, self).__init__(*args, **kwargs)
