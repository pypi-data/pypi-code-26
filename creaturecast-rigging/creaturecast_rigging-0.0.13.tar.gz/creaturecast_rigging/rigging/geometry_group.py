import creaturecast_rigging.nodes.transform as trn


class GeometryGroup(trn.Transform):

    default_data = dict(
        icon='geometry',
        suffix='ggp',
        base_type='geometryGroup'
    )

    def __init__(self, *args, **kwargs):

        super(GeometryGroup, self).__init__(*args, **kwargs)


