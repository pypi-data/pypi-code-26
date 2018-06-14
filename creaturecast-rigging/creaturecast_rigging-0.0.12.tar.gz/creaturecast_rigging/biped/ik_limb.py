import copy

import creaturecast_rigging.rigging.connect_curve as ccv
import creaturecast_rigging.rigging.template as tpt
import creaturecast_rigging.math.matrix as mtx
import creaturecast_rigging.rigging.constraint as cnt
import creaturecast_rigging.rigging.handle as hdl
import creaturecast_rigging.rigging.joint_array as jry
import creaturecast_rigging.rigging.kinematics as kin
import creaturecast_rigging.rigging.part as prt
import creaturecast_node.node as nod


class IkLimbTemplate(prt.PartTemplate):

    default_data = dict(
        icon='left_arm',
        root_name='limb',
        suffix='lmb',
        count=4
    )

    def __init__(self, *args, **kwargs):
        super(IkLimbTemplate, self).__init__(*args, **kwargs)
        self.constructor = IkLimb

    def create(self):
        super(IkLimbTemplate, self).create()

        root_name = self.data['root_name']
        index_name = nod.name_handler.get_index_name(**self.data)
        side = self.data['side']
        size = self.data['size']

        template_chain = tpt.ChainTemplate(
            root_name=root_name,
            parent=self,
            matrices=self.matrices[0:-2]
        ).create()

        aim_constraints = list(template_chain.nodes['joint_aim_constraints'])
        joints = list(template_chain.nodes['joints'])
        handles = list(template_chain.nodes['handles'])

        up_handle_a = tpt.Sphere(
            index=1,
            root_name='%s_up' % index_name,
            parent=self,
            node_type='joint',
            matrix=self.matrices[-2]
        ).create()

        up_handle_b = tpt.Sphere(
            index=2,
            root_name='%s_up' % index_name,
            parent=self,
            node_type='joint',
            matrix=self.matrices[-1]
        ).create()


        connect_curve_a = ccv.create_connect_curve(
            handles[1],
            up_handle_a,
            parent=self,
            index=0,
        )

        connect_curve_b = ccv.create_connect_curve(
            handles[1],
            up_handle_a,
            parent=self,
            index=1,
            name='%s_connect' % root_name
        )

        connect_curve_c = ccv.create_connect_curve(
            handles[2],
            up_handle_b,
            parent=self,
            index=2,
            name='%s_connect' % root_name
        )

        up_handle_a.plugs['worldMatrix'].connect_to(aim_constraints[0].plugs['worldUpMatrix'])
        up_handle_a.plugs['worldMatrix'].connect_to(aim_constraints[1].plugs['worldUpMatrix'])
        up_handle_b.plugs['worldMatrix'].connect_to(aim_constraints[2].plugs['worldUpMatrix'])
        self.plugs['size'].connect_to(template_chain.plugs['size'])
        self.plugs['size'].connect_to(up_handle_a.plugs['size'])
        self.plugs['size'].connect_to(up_handle_b.plugs['size'])

        for constraint in aim_constraints:
            constraint.plugs['worldUpType'].set_value(1)

        handles.extend([up_handle_a, up_handle_b])

        self.nodes['handles'] = handles
        self.nodes['joints'] = joints
        self.nodes['template_chain'] = template_chain

        return self


class IkLimb(prt.Part):

    default_data = copy.copy(prt.Part.default_data)
    default_data.update(dict(
        icon='left_arm',
        root_name='limb',
        suffix='lmb',
        count=4

    ))

    def __init__(self, *args, **kwargs):
        super(IkLimb, self).__init__(*args, **kwargs)
        self.constructor = IkLimbTemplate

    def create(self):
        super(IkLimb, self).create()

        root_name = self.data['root_name']
        size = self.data['size']
        matrices = self.matrices

        base_translate = list(matrices[0].get_translate())
        base_matrix = mtx.Matrix()
        base_matrix.set_translate(base_translate)

        root_handle = hdl.Handle(
                root_name='%s_root' % root_name,
                parent=self,
                shape='cube',
                matrix=base_matrix.values
        ).create()
        root_handle.add_group()

        joint_array = jry.JointArray(
                root_name=root_name,
                parent=self,
                matrices=matrices,
                parent_as_chain=True,
                size=size*0.25
        ).create()

        joints = joint_array.nodes['items']

        end_handle = hdl.Handle(
            root_name='%s_end' % root_name,
            parent=self,
            shape='cube',
            node_type='joint',
            matrix=matrices[2].values
        ).create()
        end_handle.add_group()

        pole_position = kin.get_pole_position(matrices, distance=5.0 * size)

        pole_handle = hdl.Handle(
            root_name='%s_pole' % root_name,
            parent=self,
            shape='diamond',
            matrix=pole_position
        ).create()

        pole_handle.add_group()

        ik_handle = kin.create_rp_handle(
            joints[0],
            joints[2],
        )

        #Take another look at this
        #end_rotate = list(matrices[0].get_rotate())
        #end_handle.plugs['jointOrientX'].set_value(end_rotate[0])
        #end_handle.plugs['jointOrientY'].set_value(end_rotate[1])
        #end_handle.plugs['jointOrientZ'].set_value(end_rotate[2])

        end_handle.plugs['drawStyle'].set_value(2)
        ik_handle.plugs['visibility'].set_value(False)
        twist_plug = end_handle.create_plug('twist', at='double', k=True)
        twist_plug.connect_to(ik_handle.plugs['twist'])

        cnt.create_point_constraint(
            root_handle,
            joints[0],
            mo=False
        )

        cnt.create_point_constraint(
            end_handle,
            ik_handle,
            mo=False
        )

        cnt.create_orient_constraint(
            end_handle,
            joints[2],
            mo=False
        )

        cnt.create_pole_vector_constraint(
            pole_handle,
            ik_handle
        )

        self.nodes['handles'] = [root_handle, end_handle, pole_handle]
        self.nodes['joints'] = joints
        self.nodes['joint_array'] = joint_array
        self.nodes['ik_handle'] = ik_handle

        return self
