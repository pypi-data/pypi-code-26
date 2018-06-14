import creaturecast_node.node as nod
import creaturecast_rigging.rigging.part_array as pay
import creaturecast_rigging.nodes.joint as jnt
import creaturecast_rigging.rigging.skeleton as skl
import creaturecast_rigging.rigging.constraint as cnt
import creaturecast_rigging.nodes.shader as shd
import creaturecast_rigging.nodes.transform as trn
import creaturecast_node.node_factory as nfc


class BodyTemplate(pay.PartArrayTemplate):

    default_data = dict(
        icon='geo_cylinder_grey',
        root_name='body',
        suffix='bdy',
        bind_skeleton=True,
        base_type='body_template',
        built=False
    )

    def __init__(self, *args, **kwargs):
        super(BodyTemplate, self).__init__(*args, **kwargs)
        #if kwargs.get('parent', None):
        #    raise Exception('Body is a root, and  shouldn\'t be parented to anything')
        self.constructor = Body

    def create(self):
        super(BodyTemplate, self).create()

        left_shader = shd.Shader(
            side=0,
            parent=self,
            specular_color=[0.0, 0.0, 0.0],
            transparency=[0.9, 0.9, 0.9],
            ambient_color=[0.5, 0.5, 0.5],
            color=nod.rig_settings['side_rgb'][0]
        ).create()

        self.nodes['left_shader'] = left_shader

        right_shader = shd.Shader(
            side=1,
            parent=self,
            specular_color=[0.0, 0.0, 0.0],
            transparency=[0.9, 0.9, 0.9],
            ambient_color=[0.5, 0.5, 0.5],
            color=nod.rig_settings['side_rgb'][1]
        ).create()

        self.nodes['right_shader'] = right_shader

        center_shader = shd.Shader(
            side=2,
            parent=self,
            specularColor=[0.0, 0.0, 0.0],
            transparency=[0.9, 0.9, 0.9],
            ambient_color=[0.5, 0.5, 0.5],
            color=nod.rig_settings['side_rgb'][2]
        ).create()

        self.nodes['center_shader'] = center_shader

        self.assign_part_shaders()
        return self

    def assign_part_shaders(self):

        for part in self.nodes['parts']:
            side = part.data['side']
            if side in [2, 3]:
                part.nodes['shader'] = self.nodes['center_shader']
            if side == 0:
                part.nodes['shader'] = self.nodes['right_shader']
            if side == 1:
                part.nodes['shader'] = self.nodes['left_shader']


class Body(pay.PartArray):

    default_data = dict(
        icon='geo_cylinder_grey',
        root_name='body',
        suffix='bdy',
        base_type='body'
    )

    def __init__(self, *args, **kwargs):

        super(Body, self).__init__(*args, **kwargs)
        if kwargs.get('parent', None):
            raise Exception('Body is a root, and  shouldn\'t be parented to anything')
        self.constructor = BodyTemplate

    def create_bind_skeleton(self):

        root_name = self.data['root_name']
        joint_size = self.data['size']*0.02
        skeleton = skl.Skeleton(
            parent=None,
            side=self.data['side'],
            size=joint_size,
            index=self.data['index'],
            root_name='%s_bind' % root_name
        ).create()
        bind_joints = []
        constraints = []
        parts = self.nodes['parts']
        for p, part in enumerate(parts):
            joints = part.get_nodes('joints')
            parent = skeleton
            part_joints = []
            for j, joint in enumerate(joints):
                bind_joint = jnt.Joint(
                    parent=parent,
                    root_name='%s_bind' % joint.data['root_name'],
                    index=joint.data['index'],
                    side=joint.data['side'],
                    size=joint.data['size'],
                    matrix=joint.matrix.values
                ).create()
                #bind_joint.plugs['displayLocalAxis'].set_value(True)
                part_joints.append(bind_joint)
                constraints.append(cnt.ParentConstraint(
                    parent=skeleton,
                    build_kwargs={'mo': False}
                ).create(
                    joint,
                    bind_joint
                ))
                draw_style = joint.plugs['drawStyle'].data.get('value', 0)
                joint.plugs['drawStyle'].set_value(2)
                bind_joint.plugs['drawStyle'].set_value(draw_style)

                bind_joint.plugs['type'].set_value(joint.plugs['type'].get_value())

                #
                #
                #
                #set t, r, s lock=True, keyable=False, channelBox=False
                #transfer joint properties to bind joint
                #
                #
                #

                parent = bind_joint
            bind_joints.append(part_joints)
        skeleton.plugs['overrideEnabled'].set_value(True)
        skeleton.plugs['overrideRGBColors'].set_value(1)
        skeleton.plugs['overrideColorRGB'].set_value(nod.rig_settings['bind_rgb'])

        for i, location in enumerate(self.get_hierarchy_map()):
            if location:
                bind_joints[i][0].set_parent(bind_joints[location[0]][location[1]])

        skeleton.nodes['constraints'] = constraints
        self.nodes['bind_skeleton'] = skeleton

        skeleton.set_parent(self)
