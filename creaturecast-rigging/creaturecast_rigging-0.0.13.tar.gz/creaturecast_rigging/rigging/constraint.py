import copy
import creaturecast_rigging.nodes.dag_node as dag


def create_pole_vector_constraint(*args, **kwargs):
    args = flatten_nodes(*args)
    return create_constraint(PoleVectorConstraint, *args, **kwargs)


def create_parent_constraint(*args, **kwargs):
    args = flatten_nodes(*args)
    return create_constraint(ParentConstraint, *args, **kwargs)


def create_aim_constraint(*args, **kwargs):
    args = flatten_nodes(*args)

    world_up_object = None

    for node_arg in ['wuo', 'worldUpObject', 'world_up_object']:
        if node_arg in kwargs:
            world_up_object = kwargs.pop(node_arg)

    constraint = create_constraint(AimConstraint, *args, **kwargs)
    if world_up_object:
        constraint.nodes['world_up_object'] = world_up_object
    return constraint


def create_tangent_constraint(*args, **kwargs):
    args = flatten_nodes(*args)
    if not args[0].data['base_type'] == 'nurbs_curve':
        raise Exception(
            'The first argument must be a NurbsCurve when creating a TangentConstraint, not %s' % type(args[0])
        )
    #if not args[0].data['positions']:
     #   raise Exception(
     #       'You must pass a NurbsCurve with a valid shape when creating a TangentConstraint'
     #   )

    world_up_object = None

    for node_arg in ['wuo', 'worldUpObject', 'world_up_object']:
        if node_arg in kwargs:
            world_up_object = kwargs.pop(node_arg)

    constraint = create_constraint(TangentConstraint, *args, **kwargs)

    if world_up_object:
        constraint.nodes['world_up_object'] = world_up_object
    return constraint


def create_orient_constraint(*args, **kwargs):
    args = flatten_nodes(*args)
    return create_constraint(OrientConstraint, *args, **kwargs)


def create_point_constraint(*args, **kwargs):
    args = flatten_nodes(*args)
    return create_constraint(PointConstraint, *args, **kwargs)


def create_constraint(constraint_class, *args, **kwargs):
    if len(args) < 2:
        raise Exception('Need at least two nodes to create a %s' % constraint_class.__name__)
    parent = args[-1]
    constraint = constraint_class(
        parent=parent,
        name='%s_%s' % (args[-1].data['name'], constraint_class.default_data['suffix'])
    )
    constraint.nodes['targets'] = args[:-1]
    constraint.nodes['transform'] = args[-1]
    constraint.data['create_kwargs'] = kwargs
    constraint.matrix = copy.copy(args[-1].matrix)
    return constraint


class AbstractConstraint(dag.DagNode):

    default_data = dict(
        icon='constraint',
        suffix='con',
        base_type='constraint',
        constraint_command=None,
        layer='constraint',
        node_type='constraint'
    )

    def __init__(self, *args, **kwargs):
        super(AbstractConstraint, self).__init__(*args, **kwargs)
        self.create_args = []
        self.create_kwargs = dict()


class PoleVectorConstraint(AbstractConstraint):

    default_data = dict(
        suffix='plcon',
        constraint_command='poleVectorConstraint'
    )

    def __init__(self, *args, **kwargs):
        super(PoleVectorConstraint, self).__init__(*args, **kwargs)


class PointConstraint(AbstractConstraint):

    default_data = dict(
        suffix='ptcon',
        constraint_command='pointConstraint'
    )

    def __init__(self, *args, **kwargs):
        super(PointConstraint, self).__init__(*args, **kwargs)


class ParentConstraint(AbstractConstraint):

    default_data = dict(
        suffix='parcon',
        constraint_command='parentConstraint'
    )

    def __init__(self, *args, **kwargs):
        super(ParentConstraint, self).__init__(*args, **kwargs)


class OrientConstraint(AbstractConstraint):

    default_data = dict(
        suffix='orcon',
        constraint_command='orientConstraint',
    )

    def __init__(self, *args, **kwargs):
        super(OrientConstraint, self).__init__(*args, **kwargs)


class TangentConstraint(AbstractConstraint):

    default_data = dict(
        suffix='tancon',
        constraint_command='tangentConstraint'
    )

    def __init__(self, *args, **kwargs):
        super(TangentConstraint, self).__init__(*args, **kwargs)


class AimConstraint(AbstractConstraint):

    default_data = dict(
        suffix='aimcon',
        constraint_command='aimConstraint'
    )

    def __init__(self, *args, **kwargs):
        super(AimConstraint, self).__init__(*args, **kwargs)


def flatten_nodes(*args):
    flattened_args = []
    for arg in args:
        if isinstance(arg, (list, tuple, set)):
            flattened_args.extend(flatten_nodes(*[x for x in arg]))
        elif isinstance(arg, dict):
            flattened_args.extend(flatten_nodes(*arg.values()))
        else:
            flattened_args.append(arg)
    return flattened_args
