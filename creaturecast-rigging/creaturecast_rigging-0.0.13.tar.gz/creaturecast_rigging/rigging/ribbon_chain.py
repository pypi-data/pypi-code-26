import creaturecast_rigging.nodes.depend_node as dep
import creaturecast_rigging.nodes.mesh as msh
import creaturecast_rigging.rigging.constraint as cnt
import creaturecast_rigging.nodes.skin_cluster as skn
import creaturecast_rigging.rigging.connect_curve as ccv
import creaturecast_rigging.rigging.template as tpt
import creaturecast_rigging.rigging.joint_array as jry
import creaturecast_rigging.rigging.ribbon as rib
import creaturecast_rigging.rigging.ribbon_handle_array as ray
import creaturecast_rigging.rigging.part as prt
import creaturecast_rigging.rigging.handle_array as hry


class RibbonChainTemplate(prt.PartTemplate):

    default_data = dict(
        icon='muscle_grey',
        suffix='rct',
        sub_structure=None,
        degree=2,
        count=4,
        form=0,
    )

    def __init__(self, *args, **kwargs):
        super(RibbonChainTemplate, self).__init__(*args, **kwargs)
        self.constructor = RibbonChain

    def create(self):
        super(RibbonChainTemplate, self).create()

        root_name = self.data['root_name']
        count = len(self.matrices)-1
        if not self.data['sub_structure']:
            self.data['sub_structure'] = [count*2-1, count*4-1]

        template_chain = tpt.ChainTemplate(
            root_name=root_name,
            parent=self,
            matrices=self.matrices[0:4]
        ).create()

        joints = list(template_chain.nodes['joints'])
        handles = list(template_chain.nodes['handles'])
        base_joints = list(joints)

        ccv.create_connect_curve(
            *joints,
            parent=self,
            index=0
        )

        up_handle = tpt.Sphere(
            node_type='joint',
            root_name='%s_up' % root_name,
            parent=self,
            matrix=self.matrices[4]
        ).create()

        #self.plugs['size'].connect_to(up_handle.plugs['size'])
        #self.plugs['size'].connect_to(template_chain.plugs['size'])

        handles.append(up_handle)

        ccv.create_connect_curve(
            joints[0],
            up_handle,
            parent=self
        )

        for constraint in template_chain.nodes['joint_aim_constraints']:
            constraint.plugs['worldUpType'].value = 1
            up_handle.plugs['worldMatrix'].connect_to(constraint.plugs['worldUpMatrix'])

        ribbon = rib.Ribbon(
            parent=self,
            positions=[x.get_translate().values for x in self.matrices[0:4]],
            direction=[1.0, 0.0, 0.0]
        )

        #ribbon.plugs.set_values(
        #    visibility=False
        #)

        ribbon_chain = ray.create_ribbon_handle_array(
            ribbon,
            parent=self,
            count=self.data['sub_structure'][-1],
            item_data=dict(
                node_type='joint'
            )
        )

        #skin_cluster = skn.create_skin_cluster(
        #    joints,
        #    ribbon
        #)

        joints = ribbon_chain.nodes['items']

        ccv.create_connect_curve(
            *joints,
            parent=self,
            index=1
        )

        for joint in joints:

            joint_index_name = joint.get_index_name()

            joint.plugs.set_values(
                overrideDisplayType=2,
                overrideEnabled=True,
                drawStyle=2
            )

            poly_sphere = dep.DependNode(
                root_name=joint_index_name,
                node_type='polySphere',
                parent=joint,
                suffix='psp'
            )

            multiply = dep.DependNode(
                root_name=joint_index_name,
                node_type='multiplyDivide',
                parent=joint,
                suffix='mlt'
            )

            mesh = msh.Mesh(
                root_name=joint_index_name,
                parent=joint,
                suffix='msh'
            )

            multiply.plugs['input1X'].value = 0.25

            poly_sphere.plugs['output'].connect_to(
                mesh.plugs['inMesh']
            )
            multiply.plugs['outputX'].connect_to(
                poly_sphere.plugs['radius']
            )
            #self.plugs['size'].connect_to(
            #    multiply.plugs['input2X']
            #)

            poly_sphere.plugs.set_values(
                subdivisionsAxis=12,
                subdivisionsHeight=8
            )

        #self.nodes['skin_cluster'] = skin_cluster
        self.nodes['joints'] = joints
        #self.nodes['base_joints'] = base_joints
        self.nodes['ribbon_chain'] = ribbon_chain
        self.nodes['ribbon'] = ribbon
        self.nodes['handles'] = handles

        return self

    def create_rig(self, parent=None):
        template_data = dict(self.data)
        rig_data = dict(self.data)

        template_data['matrices'] = [x.matrix.values for x in self.nodes['handles']]
        rig_data['matrices'] = [x.matrix.values for x in self.nodes['base_joints']]

        rig_data.update(
            template_data=template_data,
            parent=parent
        )

        rig_data['created'] = False
        self.delete()

        rig = self.constructor(**rig_data)
        rig.create()
        return rig


class RibbonChain(prt.Part):

    default_data = dict(
        icon='muscle_grey',
        root_name='muscle',
        suffix='rcn',
        sub_structure=None,
        degree=2,
        parent_as_chain=False
    )

    def __init__(self, *args, **kwargs):
        super(RibbonChain, self).__init__(*args, **kwargs)
        self.constructor = RibbonChainTemplate

    def create(self, **kwargs):
        super(RibbonChain, self).create()
        sub_structure = self.data['sub_structure']
        size = self.data['size']
        matrices = self.matrices

        handle_array = hry.HandleArray(
                parent=self,
                matrices=matrices[0:-1],
                parent_as_chain=True,
                item_data=dict(
                    node_type='transform',
                    shape='cube',
                )
        ).create()

        joint_array = jry.JointArray(
                parent=self,
                matrices=matrices,
                parent_as_chain=False,
                size=size*0.25
        ).create()

        handles = handle_array.nodes['items']
        base_joints = joint_array.nodes['items']
        joints = base_joints
        handles[-1].plugs['visibility'].value = False
        handle_array.create_lengthy_handles()
        handle_array.add_groups(1)

        #skin_clusters = []
        handle_arrays = [handle_array]

        for i, handle in enumerate(handles):

            cnt.create_parent_constraint(
                handles[i],
                base_joints[i],
                mo=False
            )

        for i, count in enumerate(sub_structure):

            ribbon = rib.Ribbon(
                parent=self,
                index=i,
                positions=[x.get_translate().values for x in matrices]
            )

            ribbon.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=1
            )

            ribbon_chain = ray.create_ribbon_handle_array(
                ribbon,
                count=count,
                parent=self,
                index=i
            )

            ribbon_handles = ribbon_chain.nodes['items']

            #skin_cluster = skn.create_skin_cluster(
            #    joints,
            #    ribbon
            #)
            #skin_clusters.append(
            #    skin_cluster
            #)
            matrices = ribbon_chain.matrices

            if i == len(sub_structure)-1:
                joints = ribbon_handles

            else:
                handles.extend(
                    ribbon_handles
                )
                handle_arrays.append(
                    ribbon_chain
                )

        #self.nodes['skin_clusters'] = skin_clusters
        self.nodes['joints'] = joints
        self.nodes['base_joints'] = base_joints
        self.nodes['handles'] = handles
        self.nodes['handle_arrays'] = handle_arrays

