import creaturecast_rigging.nodes.nurbs_curve as ncv


def create_connect_curve(*transforms, **kwargs):
    positions = [x.matrix.get_translate().values for x in transforms]
    spans = len(positions)-1
    knots = ncv.calculate_knots(spans, 1, 0)

    curve_kwargs = dict(
            degree=1,
            spans=spans,
            form=0,
            rational=False,
            dimension=3,
            knots=knots,
            two_dimensional=False,
            positions=positions,
            root_name='%s_connect' % transforms[0].data['root_name']
        )

    curve_kwargs.update(
        kwargs
    )

    curve = ncv.NurbsCurve(
        **curve_kwargs
    )

    curve.plugs.set_values(
        overrideDisplayType=2,
    )

    curve.plugs.set_values(
        overrideDisplayType=1,
        overrideEnabled=True
    )

    for i in range(len(positions)):
        transforms[i].plugs['translate'].connect_to(
            curve.plugs['cv[%s]' % i]
        )

    return curve

