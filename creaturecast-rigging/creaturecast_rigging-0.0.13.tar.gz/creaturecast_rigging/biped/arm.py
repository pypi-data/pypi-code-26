import creaturecast_rigging.rigging.connect_curve as ccv
import creaturecast_rigging.rigging.template as tpt
import creaturecast_rigging.rigging.part as prt
import creaturecast_rigging.rigging.constraint as cnt
import creaturecast_rigging.rigging.handle as hdl
import creaturecast_rigging.biped.limb as lim
import creaturecast_rigging.biped.shoulder as sdr

class ArmTemplate(prt.PartTemplate):

    default_data = dict(
        icon='/images/icons/left_arm.png',
        root_name='arm',
        suffix='arm',
    )

    def __init__(self, *args, **kwargs):
        super(ArmTemplate, self).__init__(*args, **kwargs)
        self.constructor = Arm

    def create(self):
        super(ArmTemplate, self).create()

        root_name = self.data['root_name']
        index_name = root_name

        template_chain = tpt.ChainTemplate(
            root_name=root_name,
            parent=self,
            matrices=self.matrices[:5]
        ).create()

        aim_constraints = list(template_chain.nodes['joint_aim_constraints'])
        joints = list(template_chain.nodes['joints'])
        handles = list(template_chain.nodes['handles'])

        up_handle_a = tpt.Sphere(
            index=0,
            root_name='%s_up' % index_name,
            parent=self,
            node_type='joint',
            matrix=self.matrices[5]
        ).create()

        up_handle_b = tpt.Sphere(
            index=2,
            root_name='%s_up' % index_name,
            parent=self,
            node_type='joint',
            matrix=self.matrices[6]
        ).create()

        up_handle_c = tpt.Sphere(
            index=3,
            root_name='%s_up' % index_name,
            parent=self,
            node_type='joint',
            matrix=self.matrices[7]

        ).create()

        ccv.create_connect_curve(
            handles[0],
            up_handle_a,
            parent=self,
            index=1
        )

        ccv.create_connect_curve(
            handles[2],
            up_handle_b,
            parent=self,
            index=2
        )

        ccv.create_connect_curve(
            handles[3],
            up_handle_c,
            parent=self,
            index=3
        )

        self.plugs['size'].connect_to(up_handle_a.plugs['size'])
        self.plugs['size'].connect_to(up_handle_c.plugs['size'])
        self.plugs['size'].connect_to(up_handle_b.plugs['size'])
        up_handle_a.plugs['worldMatrix'].connect_to(aim_constraints[0].plugs['worldUpMatrix'])
        up_handle_b.plugs['worldMatrix'].connect_to(aim_constraints[1].plugs['worldUpMatrix'])
        up_handle_b.plugs['worldMatrix'].connect_to(aim_constraints[2].plugs['worldUpMatrix'])
        up_handle_c.plugs['worldMatrix'].connect_to(aim_constraints[3].plugs['worldUpMatrix'])
        up_handle_c.plugs['worldMatrix'].connect_to(aim_constraints[4].plugs['worldUpMatrix'])

        for constraint in aim_constraints:
            constraint.plugs['worldUpType'].value = 1

        handles.extend([
            up_handle_a,
            up_handle_b,
            up_handle_c
        ])

        self.nodes['core_handles'] = list(handles)
        self.nodes['handles'] = handles
        self.nodes['joints'] = joints

        return self


class Arm(prt.Part):

    default_data = dict(
        icon='left_arm',
        root_name='arm',
        suffix='arm',
    )

    def __init__(self, *args, **kwargs):
        super(Arm, self).__init__(*args, **kwargs)
        self.constructor = ArmTemplate

    def create(self):
        super(prt.Part, self).create()
        root_name = self.data['root_name']
        matrices = self.matrices
        size = self.data['size']

        shoulder = sdr.Shoulder(
            matrices=matrices[:2],
            root_name='%s_shoulder' % root_name,
            parent=self
        ).create()

        limb = lim.Limb(
            matrices=matrices[1:],
            root_name='%s_limb' % root_name,
            parent=self,
            size=size
        ).create()

        joints = list(shoulder.nodes['joints'])
        joints.extend(limb.nodes['joints'])
        handles = shoulder.nodes['handles']
        handles.extend(limb.nodes['handles'])

        limb.set_parent(joints[1])

        self.nodes['shoulder'] = shoulder
        self.nodes['limb'] = limb
        self.nodes['joints'] = joints
        self.nodes['handles'] = handles

        return self

    def create_human_ik_skeleton(self, parent=None):
        size = self.data['size']
        side = self.data['side']
        shoulder = self.nodes['shoulder']
        fk_limb = self.nodes['limb'].nodes['fk_limb']
        fk_handles = [shoulder.nodes['handles'][0]]
        fk_handles.extend(fk_limb.get_nodes('handles'))

        new_joints = []
        for i, handle in enumerate(fk_handles):

            new_joint = hdl.Handle(
                root_name='%s_human_ik' % handle.data['root_name'],
                index=handle.data['index'],
                side=handle.data['side'],
                size=size*0.1,
                matrix=handle.matrix.values,
                shape='cube',
                node_type='joint'
            ).create()

            new_joint.plugs['drawStyle'].set_value(2)
            side_dictionary = {0: 0, 1: 1, -1: 2, 2: 0}

            cnt.create_parent_constraint(
                new_joint,
                handle,
                mo=False
            )

            if i != 0:
                new_joint.set_parent(new_joints[-1])
                new_joint.plugs['side'].set_value(side_dictionary[side])
                new_joints[i - 1].create_lengthy_handle(new_joint)

            else:
                new_joint.plugs['side'].set_value(side_dictionary[side])

            new_joint.plugs['type'].set_value(7)

            new_joints.append(new_joint)

        if parent:
            new_joints[0].set_parent(parent)

        return new_joints
