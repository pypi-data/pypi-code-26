import creaturecast_rigging.nodes.nurbs_surface as nsf


class Ribbon(nsf.NurbsSurface):

    default_data = dict(
        icon='grey_ribbon',
        base_type='ribbon',
        layer='geometry',
        degree=3,
        direction=[0.0, 0.0, -1.0],
        positions=[
            [0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 2.0, 0.0],
            [0.0, 3.0, 0.0],
            [0.0, 4.0, 0.0]
        ]
    )

    def __init__(self, *args, **kwargs):

        super(Ribbon, self).__init__(*args, **kwargs)

    def create(self):
        super(Ribbon, self).create()
        return self

