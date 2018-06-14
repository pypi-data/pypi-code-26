import creaturecast_rigging.math.matrix as mtx
import creaturecast_rigging.rigging.handle as hdl
import creaturecast_rigging.rigging.fk_chain as fkc
import creaturecast_rigging.rigging.joint_array as jry
import creaturecast_rigging.rigging.part as prt
import creaturecast_rigging.biped.ik_leg as ikl
import creaturecast_node.node as nod

rig_settings = nod.rig_settings


class LegTemplate(ikl.IkLegTemplate):

    default_data = dict(
        icon='left_leg',
        root_name='leg',
        suffix='leg',
    )

    def __init__(self, *args, **kwargs):
        kwargs['count'] = 5
        super(LegTemplate, self).__init__(*args, **kwargs)
        self.constructor = Leg


class Leg(prt.Part):

    default_data = dict(
        icon='left_leg',
        root_name='leg',
        suffix='leg',
    )

    def __init__(self, *args, **kwargs):
        super(Leg, self).__init__(*args, **kwargs)
        self.constructor = LegTemplate

    def create(self):
        super(prt.Part, self).create()
        root_name = self.data['root_name']
        matrices = self.matrices
        size = self.data['size']
        side = self.data['side']

        ik_leg = ikl.IkLeg(
            matrices=matrices,
            root_name='%s_limb' % root_name,
            parent=self,
            size=size
        ).create()

        fk_leg = fkc.FkChain(
            matrices=matrices,
            root_name='%s_toe' % root_name,
            parent=self,
            size=size
        ).create()

        joint_array = jry.JointArray(
                root_name=root_name,
                parent=self,
                matrices=matrices,
                parent_as_chain=True,
                size=size*0.25
        ).create()

        joints = joint_array.get_nodes('items')

        attr_matrix = mtx.Matrix()
        attr_matrix.set_translate(matrices[2].get_translate())

        attr_handle = hdl.Handle(
                root_name='%s_attr' % root_name,
                parent=joints[2],
                shape='pointer',
                matrix=attr_matrix,
                size=size
        ).create()

        ik_joints = ik_leg.get_nodes('joints')
        fk_joints = fk_leg.get_nodes('joints')
        ik_joint_array = ik_leg.get_node('joint_array')
        fk_joint_array = fk_leg.get_node('joint_array')


        blend_plug = attr_handle.create_plug('ik_blend', at='double', k=True, min=0.0, max=1.0)
        attr_handle_rotation = [x*y for x, y in zip([-90.0]*3, rig_settings.get_side_up_vector(side))]
        attr_handle.plugs['rotate'].set_value(attr_handle_rotation)

        for itr, joint in enumerate(joints[0:-1]):

            pair_blend = dep.DependNode(
                    node_type='pairBlend',
                    root_name=root_name,
                    parent=self,
                    suffix='pbl'
            ).create()
            fk_joints[itr].plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
            ik_joints[itr].plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
            fk_joints[itr].plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
            ik_joints[itr].plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
            pair_blend.plugs['outTranslate'].connect_to(joint.plugs['translate'])
            pair_blend.plugs['outRotate'].connect_to(joint.plugs['rotate'])
            blend_plug.connect_to(pair_blend.plugs['weight'])

        reverse_node = dep.DependNode(
                node_type='reverse',
                root_name=root_name,
                parent=self,
                suffix='rev'
        ).create()

        ik_joint_array.plugs['visibility'].set_value(False)
        fk_joint_array.plugs['visibility'].set_value(False)
        blend_plug.connect_to(reverse_node.plugs['inputX'])
        blend_plug.connect_to(ik_limb.plugs['v'])
        reverse_node.plugs['outputX'].connect_to(fk_limb.plugs['v'])

        self.set_node('ik_leg', ik_leg)
        self.set_node('fk_leg', fk_leg)
        self.add_nodes('joints', joints)

        return self

