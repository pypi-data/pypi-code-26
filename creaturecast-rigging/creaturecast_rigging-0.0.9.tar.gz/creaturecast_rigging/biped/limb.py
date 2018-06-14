import creaturecast_rigging.rigging.fk_chain as fkc
import creaturecast_rigging.biped.ik_limb as ikl
import creaturecast_rigging.math.matrix as mtx
import creaturecast_rigging.nodes.depend_node as dep
import creaturecast_rigging.rigging.handle as hdl
import creaturecast_rigging.rigging.joint_array as jry
import creaturecast_rigging.rigging.part as prt
import creaturecast_rigging.utilities as rut


class LimbTemplate(ikl.IkLimbTemplate):

    default_data = dict()

    def __init__(self, *args, **kwargs):
        super(LimbTemplate, self).__init__(*args, **kwargs)
        self.constructor = Limb


class Limb(ikl.IkLimb):

    default_data = dict()

    def __init__(self, *args, **kwargs):
        super(Limb, self).__init__(*args, **kwargs)
        self.constructor = LimbTemplate

    def create(self):
        super(prt.Part, self).create()
        root_name = self.data['root_name']
        side = self.data['side']

        matrices = self.matrices

        size = self.data['size']

        ik_limb = ikl.IkLimb(
            matrices=matrices,
            root_name='%s_ik' % root_name,
            parent=self,
        ).create()

        fk_limb = fkc.FkChain(
            matrices=matrices,
            root_name='%s_fk' % root_name,
            parent=self,
        ).create()

        ik_joints = ik_limb.nodes['joints']
        fk_joints = fk_limb.nodes['joints']
        ik_joint_array = ik_limb.nodes['joint_array']
        fk_joint_array = fk_limb.nodes['joint_array']

        joint_array = jry.JointArray(
                root_name='%s_bind' % root_name,
                parent=self,
                matrices=matrices,
                parent_as_chain=True,
                size=size*0.25
        ).create()

        joints = joint_array.nodes['items']

        attr_matrix = mtx.Matrix()
        attr_matrix.set_translate(matrices[2].get_translate())

        attr_handle = hdl.Handle(
                root_name='%s_attr' % root_name,
                parent=joints[2],
                shape='pointer',
                matrix=attr_matrix,
                size=size
        ).create()

        blend_plug = attr_handle.create_plug('ik_blend', at='double', k=True, min=0.0, max=1.0)
        attr_handle_rotation = [x*y for x, y in zip([-90.0]*3, rut.get_side_up_vector(side))]
        attr_handle.plugs['rotate'].set_value(attr_handle_rotation)

        for i, joint in enumerate(joints[0:-1]):

            pair_blend = dep.DependNode(
                    node_type='pairBlend',
                    root_name=root_name,
                    parent=self,
                    suffix='pbl',
                    index=i
            )

            fk_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
            ik_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
            fk_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
            ik_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
            pair_blend.plugs['outTranslate'].connect_to(joint.plugs['translate'])
            pair_blend.plugs['outRotate'].connect_to(joint.plugs['rotate'])
            blend_plug.connect_to(pair_blend.plugs['weight'])

        reverse_node = dep.DependNode(
                node_type='reverse',
                root_name=root_name,
                parent=self,
                suffix='rev'
        )

        ik_joint_array.plugs['visibility'].set_value(False)
        fk_joint_array.plugs['visibility'].set_value(False)
        blend_plug.connect_to(reverse_node.plugs['inputX'])
        blend_plug.connect_to(ik_limb.plugs['v'])
        reverse_node.plugs['outputX'].connect_to(fk_limb.plugs['v'])

        '''
        root_joint = jnt.Joint(
            parent=joint_array,
            root_name='%s_root' % root_name,
            matrix=joints[0].matrix.values
        ).create()

        end_root_joint = jnt.Joint(
            parent=root_joint,
            root_name='%s_root_end' % root_name,
            matrix=joints[1].matrix.values
        ).create()

        root_joint.plugs['displayLocalAxis'].set_value(True)
        end_root_joint.plugs['displayLocalAxis'].set_value(True)

        ik_handle = kin.RpHandle(
            root_name='%s_root' % root_name,
            parent=joints[0]
        ).create(
            root_joint,
            end_root_joint
        )

        ik_handle.plugs['poleVector'].set_value([0.0, 0.0, 0.0])
        #ik_handle.plugs['visibility'].set_value(False)

        joints[0].set_node('root_joint', root_joint)
        '''
        handles = ik_limb.nodes['handles']
        handles.extend(fk_limb.nodes['handles'])
        handles.append(attr_handle)

        self.nodes['fk_limb'] = fk_limb
        self.nodes['ik_limb'] = ik_limb
        self.nodes['joints'] = joints
        self.nodes['handles'] = handles
        return self
