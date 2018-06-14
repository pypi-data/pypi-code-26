import creaturecast_rigging.nodes.dag_node as dag


class NurbsCurve(dag.DagNode):

    default_data = dict(
        suffix='ncv',
        icon='nurbs_curve',
        node_type='nurbsCurve',
        base_type='nurbs_curve',
        positions=[],
        degree=3,
        demension=3,
        form=0,
        knots=[],
        number_of_spans=0,
        rational=False
    )

    def __init__(self, *args, **kwargs):
        super(NurbsCurve, self).__init__(*args, **kwargs)



def calculate_knots(spans, degree, form):

    knots = []
    knot_count = spans + 2*degree -1

    if form == 2:
        pit = (degree-1)*-1
        for itr in range(knot_count):
            knots.append(pit)
            pit += 1
        return knots

    for itr in range(degree):
        knots.append(0)
    for itr in range(knot_count - (degree*2)):
        knots.append(itr+1)
    for kit in range(degree):
        knots.append(itr+2)
    return knots

