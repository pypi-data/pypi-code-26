import creaturecast_rigging.rigging.geometry_group as gog


class AlembicNode(gog.GeometryGroup):

    default_data = dict(
        suffix='abc'
    )

    def __init__(self, *args, **kwargs):
        self.component = kwargs.pop('component', None)
        super(AlembicNode, self).__init__(*args, **kwargs)


