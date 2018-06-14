import copy

import rigging.connect_curve as ccv
import rigging.template as tpt
import rigging.template as tmp
import creaturecast_rigging.math.matrix as mtx
import creaturecast_rigging.rigging.handle as hdl
import creaturecast_rigging.rigging.joint_array as jry
import creaturecast_rigging.rigging.kinematics as kin
import creaturecast_rigging.rigging.part as prt
import creaturecast_rigging.nodes.transform as trn
import creaturecast_rigging.rigging.transform_array as tay
import creaturecast_rigging.rigging.constraint as cnt


class IkLegTemplate(tpt.ChainTemplate):

    default_data = dict(
        icon='left_leg',
        root_name='leg',
        suffix='leg',
    )

    def __init__(self, *args, **kwargs):
        kwargs['count'] = 5
        super(IkLegTemplate, self).__init__(*args, **kwargs)
        self.constructor = IkLeg

    def create(self):
        super(IkLegTemplate, self).create()

        root_name = self.data['root_name']
        index_name = self.get_index_name()
        size = self.data['size']
        side = self.data['side']


        joints = self.get_nodes('joints')
        handles = self.get_nodes('handles')
        core_handles = copy.copy(handles)
        aim_constraints = self.get_nodes('joint_aim_constraints')

        up_handle_a = tpt.Sphere(
            index=1,
            root_name='%s_up' % index_name,
            parent=self,
            node_type='joint'
        ).create()

        up_handle_a.get_node('mesh').set_node('shader', shader)

        self.plugs['size'].connect_to(up_handle_a.plugs['size'])
        handles.append(up_handle_a)

        ccv.ConnectCurve(
            parent=self,
            index=1,
        ).create(handles[1], up_handle_a)

        up_handle_a.plugs['worldMatrix'].connect_to(aim_constraints[0].plugs['worldUpMatrix'])
        up_handle_a.plugs['worldMatrix'].connect_to(aim_constraints[1].plugs['worldUpMatrix'])

        up_handle_b = tpt.Sphere(
            index=2,
            root_name='%s_up' % index_name,
            parent=self,
            node_type='joint'
        ).create()

        up_handle_b.get_node('mesh').set_node('shader', shader)

        self.plugs['size'].connect_to(up_handle_b.plugs['size'])
        handles.append(up_handle_b)

        ccv.ConnectCurve(
            parent=self,
            index=1,
        ).create(handles[2], up_handle_b)

        up_handle_b.plugs['worldMatrix'].connect_to(aim_constraints[2].plugs['worldUpMatrix'])
        up_handle_b.plugs['worldMatrix'].connect_to(aim_constraints[3].plugs['worldUpMatrix'])
        up_handle_b.plugs['worldMatrix'].connect_to(aim_constraints[4].plugs['worldUpMatrix'])

        for constraint in aim_constraints:
            constraint.plugs['worldUpType'].set_value(1)

        cones = []
        pivot_handles = []

        pivot_names = ['front', 'back', 'in', 'out']

        foot_name = '%s_foot' % root_name
        for i in range(4):
            handle = hdl.Handle(
                icon='cone',
                node_type='joint',
                parent=self,
                root_name='%s_%s' % (foot_name, pivot_names[i]),
            ).create()

            cone = tmp.Cone(
                root_name='%s_%s' % (foot_name, pivot_names[i]),
                parent=self,
                size=size*0.5,
                aim_vector=[1, 0, 0],
                node_type='transform'
            ).create()

            handle.plugs['translate'].connect_to(cone.plugs['translate'])

            multiply_divide = dep.DependNode(
                parent=handle,
                node_type='multiplyDivide'
            ).create()

            self.plugs['size'].connect_to(multiply_divide.plugs['input1X'])
            multiply_divide.plugs['input2X'].set_value(0.5)
            multiply_divide.plugs['outputX'].connect_to(handle.plugs['size'])
            multiply_divide.plugs['outputX'].connect_to(cone.plugs['size'])

            cone.get_node('mesh').set_node('shader', alt_shader)
            #handle.plugs['overrideEnabled'].set_value(True)
            #handle.plugs['overrideRGBColors'].set_value(1)
            #handle.plugs['overrideColorRGB'].set_value(nod.rig_settings['alternate_rgb'])
            cones.append(cone)
            pivot_handles.append(handle)
            #cone.plugs['displayLocalAxis'].set_value(True)

        cnt.AimConstraint(
            parent=self,
            build_kwargs={
                'mo': False,
                'aimVector': [-1, 0, 0],
                'upVector': [0, 1, 0],
                'worldUpType': 'scene'
            }).create(
            cones[0],
            cones[1],
        )
        cnt.AimConstraint(
            parent=self,
            build_kwargs={
                'mo': False,
                'aimVector': [-1, 0, 0],
                'upVector': [0, -1, 0],
                'worldUpType': 'scene'

            }).create(
            cones[1],
            cones[0],
        )
        cnt.AimConstraint(
            parent=self,
            build_kwargs={
                'mo': False,
                'aimVector': [-1, 0, 0],
                'upVector': [0, -1, 0],
                'worldUpType': 'scene'
            }).create(
            cones[2],
            cones[3],
        )
        cnt.AimConstraint(
            parent=self,
            build_kwargs={
                'mo': False,
                'aimVector': [-1, 0, 0],
                'upVector': [0, 1, 0],
                'worldUpType': 'scene'
            }).create(
            cones[3],
            cones[2],
        )

        ccv.ConnectCurve(
            parent=self,
            index=1,
        ).create(pivot_handles[0], pivot_handles[1])

        ccv.ConnectCurve(
            parent=self,
            index=1,
        ).create(pivot_handles[2], pivot_handles[3])

        handles.extend(pivot_handles)

        self.set_nodes('core_handles', core_handles)
        self.set_nodes('pivot_joints', cones)
        self.set_nodes('joints', joints)
        self.set_nodes('handles', handles)

        return self

    def _create_rig(self, parent=None):

        template_data = self.serialize()
        rig_data = copy.copy(self.data)
        matrices = [x.update_matrix().values for x in self.get_nodes('joints')]
        matrices.extend([x.update_matrix().values for x in self.get_nodes('pivot_joints')])

        rig_data.update(
            template_data=template_data,
            parent=parent,
            matrices=matrices
        )
        rig = self.constructor(**rig_data)
        rig.create()

        return rig


class IkLeg(prt.Part):

    default_data = copy.copy(prt.Part.default_data)
    default_data.update(dict(
        icon='left_leg',
        root_name='leg',
        suffix='leg',
    ))

    def __init__(self, *args, **kwargs):
        super(IkLeg, self).__init__(*args, **kwargs)
        self.constructor = IkLegTemplate

    def create(self):
        super(IkLeg, self).create()
        root_name = self.data['root_name']
        matrices = self.matrices[:5]
        pivot_matrices = self.matrices[5:]
        size = self.data['size']
        side = self.data['size']

        base_translate = matrices[0].get_translate()
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

        joints = joint_array.get_nodes('items')

        end_handle = hdl.Handle(
            root_name='%s_end' % root_name,
            parent=self,
            shape='cube',
            node_type='joint',
            matrix=matrices[2].values
        ).create()
        end_handle.add_group()


        end_handle.add_group()

        # Solve IK world/local space jointOrient trick

        #end_rotate = list(matrices[0].get_rotate())
        #end_handle.plugs['jointOrientX'].set_value(end_rotate[0])
        #end_handle.plugs['jointOrientY'].set_value(end_rotate[1])
        #end_handle.plugs['jointOrientZ'].set_value(end_rotate[2])

        try:
            pole_position = kin.get_pole_position(matrices, distance=5.0 * size)
        except kin.LengthException, e:
            raise kin.LengthException(
                '%s has a total length of zero.\n%s\'s must have non-zero length in order to calculate pole vector position.' % (self.__class__.__name__, self.__class__.__name__)
            )

        pole_handle = hdl.Handle(
            root_name='%s_pole' % root_name,
            parent=self,
            shape='diamond',
            matrix=pole_position
        ).create()

        pole_handle.add_group()

        cnt.PointConstraint(
            parent=self,
            build_kwargs={'mo': False}
        ).create(
            root_handle,
            joints[0]
        )

        cnt.OrientConstraint(
            parent=self,
            build_kwargs={'mo': False},
        ).create(
            end_handle,
            joints[2]
        )

        foot_name = '%s_foot' % root_name

        pivot_array = tay.TransformArray(
            root_name='%s_pivot' % foot_name,
            parent=end_handle,
            matrices=pivot_matrices,
            parent_as_chain=True,
            size=size * 0.25
        ).create()

        pivots = pivot_array.get_nodes('items')

        toe_pivot = trn.Transform(
            root_name='%s_toe_pivot' % foot_name,
            index=1,
            parent=pivots[-1],
        )

        toe_pivot_matrix = mtx.triangulate_matrix(
            matrices[3].get_translate(),
            matrices[4].get_translate(),
            up_vector=[0.0, -1.0, 0.0]
        )

        toe_pivot.set_world_matrix(toe_pivot_matrix)

        pivots.append(toe_pivot)

        for i, pivot in enumerate(pivots):
            #pivot.plugs['displayLocalAxis'].set_value(True)
            pivot_group = trn.Transform(
                root_name=pivot.get_index_name(),
                index=1,
                parent=pivot.parent,
                matrix=pivot.matrix
            )
            pivot.set_parent(pivot_group)

        front_pivot, back_pivot, in_pivot, out_pivot, toe_pivot = pivots

        toe_handle = hdl.Handle(
            root_name='%s_toe' % root_name,
            parent=out_pivot,
            shape='cube',
            size=size,
            matrix=matrices[3].values
        ).create()

        toe_handle.create_lengthy_handle(joints[-1])
        toe_groups = toe_handle.add_groups(2)

        handles = [root_handle, end_handle, pole_handle, toe_handle]

        roll_plug = end_handle.create_plug('roll', at='double', k=True)
        toe_plug = end_handle.create_plug('toe', at='double', k=True)
        tip_plug = end_handle.create_plug('tip', at='double', k=True, min=0)
        tilt_plug = end_handle.create_plug('tilt', at='double', k=True)
        ball_tilt_plug = end_handle.create_plug('ballTilt', at='double', k=True)
        tip_tilt_plug = end_handle.create_plug('tipTilt', at='double', k=True)

        # ball_tilt_plug.connectTo(toePivot.plugs['rotateY'])
        tip_plug.connect_to(front_pivot.plugs['rotateZ'])
        tip_tilt_plug.connect_to(front_pivot.plugs['rotateY'])
        ball_tilt_plug.connect_to(toe_pivot.plugs['rotateY'])
        toe_plug.connect_to(toe_groups[-1].plugs['rotateX'])
        #ball_tilt_plug.connect_to(toe_pivot.plugs['rotateZ'])

        heel_roll_condition = dep.DependNode(
            root_name='%s_heel_roll' % root_name,
            node_type='condition',
            parent=self
        )

        heel_roll_condition.plugs['operation'].set_value(4)
        roll_plug.connect_to(heel_roll_condition.plugs['firstTerm'])
        roll_plug.connect_to(heel_roll_condition.plugs['colorIfTrueR'])
        heel_roll_condition.plugs['outColorR'].connect_to(back_pivot.plugs['rotateZ'])

        toe_roll_condition = dep.DependNode(
            root_name='%s_toe_roll' % root_name,
            node_type='condition',
            parent=self
        )

        toe_roll_condition.plugs['operation'].set_value(2)
        roll_plug.connect_to(toe_roll_condition.plugs['firstTerm'])
        roll_plug.connect_to(toe_roll_condition.plugs['colorIfTrueR'])
        toe_roll_condition.plugs['outColorR'].connect_to(toe_pivot.plugs['rotateZ'])



        tilt_in_condition = dep.DependNode(
            root_name='%s_tilt_out' % root_name,
            node_type='condition',
            parent=self
        )

        tilt_in_condition.plugs['operation'].set_value(4)
        tilt_plug.connect_to(tilt_in_condition.plugs['firstTerm'])
        tilt_plug.connect_to(tilt_in_condition.plugs['colorIfTrueR'])
        tilt_in_condition.plugs['outColorR'].connect_to(in_pivot.plugs['rotateZ'])

        tilt_out_condition = dep.DependNode(
            root_name='%s_tilt_in' % root_name,
            node_type='condition',
            parent=self
        )

        tilt_out_condition.plugs['operation'].set_value(2)
        tilt_plug.connect_to(tilt_out_condition.plugs['firstTerm'])
        tilt_plug.connect_to(tilt_out_condition.plugs['colorIfTrueR'])
        tilt_out_condition.plugs['outColorR'].connect_to(out_pivot.plugs['rotateZ'])

        ik_handle_a = kin.RpHandle(
            root_name=root_name,
            parent=self,
            index=1
        ).create(
            joints[0],
            joints[2]
        )

        ik_handle_b = kin.RpHandle(
            root_name=root_name,
            parent=self,
            index=2,
            node_type='scHandle'

        ).create(
            joints[2],
            joints[3]
        )

        ik_handle_c = kin.RpHandle(
            root_name=root_name,
            parent=self,
            index=3,
            node_type='scHandle'
        ).create(
            joints[3],
            joints[4]
        )

        end_handle.plugs['drawStyle'].set_value(2)

        twist_plug = end_handle.create_plug('twist', at='double', k=True)
        twist_plug.connect_to(ik_handle_a.plugs['twist'])

        cnt.PoleVectorConstraint(
            parent=self,
        ).create(
            pole_handle,
            ik_handle_a
        )

        ik_handle_a.set_parent(toe_pivot)
        ik_handle_b.set_parent(out_pivot)
        ik_handle_c.set_parent(toe_handle)

        ik_handle_a.plugs['visibility'].set_value(False)
        ik_handle_b.plugs['visibility'].set_value(False)
        ik_handle_c.plugs['visibility'].set_value(False)

        self.set_nodes('joints', joints)
        self.set_nodes('handles', handles)
        self.set_nodes('ik_handles', [ik_handle_a, ik_handle_b, ik_handle_c])


        return self


    def create_human_ik_skeleton(self, parent=None):
        super(IkLeg, self).create_human_ik_skeleton()

        side = self.data['side']
        size = self.data['size']

        joints = self.get_nodes('joints')
        handles = self.get_nodes('handles')

        new_joints = []
        for i, joint in enumerate(joints):

            new_joint = hdl.Handle(
                root_name='%s_human_ik' % joint.data['root_name'],
                index=joint.data['index'],
                side=joint.data['side'],
                size=size*0.1,
                matrix=joint.matrix.values,
                shape='cube',
                node_type='joint'
            ).create()
            new_joint.plugs['drawStyle'].set_value(2)

            side_dictionary = {0: 0, 1: 1, -1: 2, 2: 0}

            if i != 0:
                new_joint.set_parent(new_joints[-1])
                new_joint.plugs['side'].set_value(side_dictionary[side])
                new_joints[i - 1].create_lengthy_handle(new_joint)

            else:
                new_joint.plugs['side'].set_value(side_dictionary[side])

            new_joints.append(new_joint)

        cnt.ParentConstraint(
            parent=parent,
            build_kwargs={'mo': False}
        ).create(
            new_joints[2],
            handles[1]
        )

        if parent:
            new_joints[0].set_parent(parent)

        return new_joints

