import copy
import creaturecast_rigging.nodes.transform as trn
import creaturecast_rigging.math.vector as vec
import creaturecast_rigging.math.matrix as mtx


def create_rp_handle(start_joint, end_joint, **kwargs):
    new_kwargs = copy.copy(end_joint.data)
    new_kwargs.update(kwargs)
    kwargs['parent'] = start_joint
    ik_handle = RpHandle(**kwargs)
    ik_handle.nodes['start_joint'] = start_joint
    ik_handle.nodes['end_joint'] = end_joint

    root_name = ik_handle.data['root_name']

    effector = trn.Transform(
        node_type='ikEffector',
        suffix='ike',
        root_name=root_name,
        parent=end_joint.parent,
        matrix=end_joint.matrix
    )

    end_joint.plugs['tx'].connect_to(effector.plugs['tx'])
    end_joint.plugs['ty'].connect_to(effector.plugs['ty'])
    end_joint.plugs['tz'].connect_to(effector.plugs['tz'])

    ik_handle.nodes['effector'] = effector

    return ik_handle


class RpHandle(trn.Transform):

    default_data = dict(
        suffix='ikh',
        node_type='ikHandle',
        icon='locator',
        base_type='ik_handle'
    )

    def __init__(self, *args, **kwargs):
        super(RpHandle, self).__init__(*args, **kwargs)


    def create(self):
        super(RpHandle, self).create()

        start_joint = self.nodes['start_joint']
        end_joint = self.nodes['end_joint']


        return self


def get_pole_position(positions, distance=5.0):

    """takes three matrices and returns a single matrix representing predicted pole vector position"""

    start = vec.Vector(*positions[0][12:15])
    mid = vec.Vector(*positions[1][12:15])
    end = vec.Vector(*positions[2][12:15])

    start_end = end - start
    start_mid = mid - start
    dot_product = start_mid.dot(start_end)
    length = start_end.length()
    if length == 0.0:
        return mtx.Matrix().values
        #raise LengthException('length is Zero.')
    #Add Exception for strait limbs
    proj = dot_product / length
    start_end_norm = start_end.normalize()
    proj_vec = start_end_norm * proj
    arrow_v = start_mid - proj_vec
    arrow_norm = arrow_v.normalize()
    arrow_dist = arrow_norm * distance
    pole_pos = arrow_dist + mid

    result = mtx.Matrix()
    result.set_translate(pole_pos)
    return result.values


class LengthException(Exception):
    def __init__(self, *args, **kwargs):
        super(LengthException, self).__init__(*args, **kwargs)

