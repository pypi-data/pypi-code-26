import creaturecast_node.node as nod
import creaturecast_rigging.math.matrix as mtx
import creaturecast_rigging.nodes.depend_node as dep
import creaturecast_rigging.nodes.locator as loc
import creaturecast_rigging.nodes.mesh as msh
import creaturecast_rigging.nodes.transform as trn
import creaturecast_rigging.rigging.constraint as cnt
import creaturecast_rigging.rigging.capsule_array as cay
import creaturecast_rigging.rigging.connect_curve as ccv
import creaturecast_rigging.rigging.handle as hdl
import creaturecast_rigging.rigging.joint_array as jry
import creaturecast_rigging.rigging.part as prt
import creaturecast_rigging.rigging.handle_array as hay
import creaturecast_rigging.utilities as utl


class ChainTemplate(prt.PartTemplate):

    default_data = dict(
        icon='chain',
        root_name='template_chain',
        suffix='tcn',
        count=4
    )

    def __init__(self, *args, **kwargs):
        super(ChainTemplate, self).__init__(*args, **kwargs)

    def create(self):

        super(ChainTemplate, self).create()

        root_name = self.data['root_name']
        size = self.data['size']
        side = self.data['side']
        count = self.data['count']

        handle_array = SphereHandleArray(
            matrices=self.matrices,
            root_name=root_name,
            count=count,
            parent=self,
            item_data=dict(
                shape=None,
                node_type='joint'
            )
        ).create()


        joint_array = jry.JointArray(
            matrices=self.matrices,
            root_name=root_name,
            count=count,
            parent_as_chain=False,
            parent=self,
            size=0.0,
        ).create()

        capsule_array = cay.CapsuleArray(
            root_name='%s_capsules' % root_name,
            count=count-1,
            parent=self
        ).create()

        #self.plugs['size'].connect_to(capsule_array.plugs['size'])
        #self.plugs['size'].connect_to(handle_array.plugs['size'])

        joints = joint_array.nodes['items']
        handles = handle_array.nodes['items']
        capsules = capsule_array.nodes['items']
        joint_aim_constraints = []
        locators = []

        for i in range(len(handles)):

            joints[i].plugs['overrideEnabled'].value = True
            joints[i].plugs['overrideDisplayType'].value = 2
            joints[i].plugs['radius'].value = 0.0

            locator = loc.Locator(
                root_name=root_name,
                index=i+1,
                parent=handles[i]
            ).create()

            locator.plugs['visibility'].set_value(False)
            locator.plugs['localScale'].value = [0, 0, 0]
            locators.append(locator)
            if i > 0:
                capsule = capsules[i-1]
                capsule.plugs['inheritsTransform'].value = False
                locators[i-1].plugs['worldPosition[0]'].connect_to(capsule.plugs['position1'])
                locators[i].plugs['worldPosition[0]'].connect_to(capsule.plugs['position2'])


        for i in range(len(handles)):

            cnt.create_point_constraint(
                handles[i],
                joints[i],
                mo=False
            )

            if i > 0:

                cnt.create_point_constraint(
                    handles[i - 1],
                    handles[i],
                    capsules[i - 1],
                    mo=False
                )

                cnt.create_aim_constraint(
                    handles[i],
                    capsules[i - 1],
                    mo=False,
                    aimVector=nod.rig_settings['aim_vector']

                )

                joint_constraint = cnt.create_aim_constraint(
                    handles[i],
                    joints[i - 1],
                    mo=False,
                    aimVector=nod.rig_settings['aim_vector']

                )

                joint_aim_constraints.append(joint_constraint)

        tip_aim_vector = [x*-1 for x in utl.get_side_aim_vector(side)]

        joint_constraint = cnt.create_aim_constraint(
            handles[-2],
            joints[-1],
            mo=False,
            aimVector=tip_aim_vector

        )

        joint_aim_constraints.append(joint_constraint)

        self.nodes['joint_aim_constraints'] = joint_aim_constraints
        self.nodes['handle_array'] = handle_array
        self.nodes['joint_array'] = joint_array
        self.nodes['joints'] = joints
        self.nodes['handles'] = handles
        self.nodes['locators'] = locators
        self.nodes['capsules'] = capsules

        return self


class UpChainTemplate(ChainTemplate):

    default_data = dict(
        suffix='uct'
    )

    def __init__(self, *args, **kwargs):
        super(UpChainTemplate, self).__init__(*args, **kwargs)

    def create(self):
        super(UpChainTemplate, self).create()

        root_name = self.data['root_name']

        up_handle = Sphere(
            root_name='%s_up' % root_name,
            parent=self,
            node_type='joint'
        ).create()

        self.nodes['handles'].append(up_handle)

        ccv.create_connect_curve(
            self.nodes['joints'][0],
            up_handle,
            parent=self
        )

        for constraint in self.nodes['joint_aim_constraints']:
            constraint.plugs['worldUpType'].set_value(1)
            up_handle.plugs['worldMatrix'].connect_to(constraint.plugs['worldUpMatrix'])

        return self


class Torus(hdl.Handle):

    default_data = dict(
        icon='torus',
        node_type='transform',
        root_name='torus_handle',

    )

    def __init__(self, *args, **kwargs):
        super(Torus, self).__init__(*args, **kwargs)

    def create(self):
        super(Torus, self).create()
        root_name = self.data['root_name']

        poly_torus = dep.DependNode(
            root_name=root_name,
            node_type='polyTorus',
            parent=self,
            suffix='pts'
        ).create()

        multiply = dep.DependNode(
            root_name=root_name,
            node_type='multiplyDivide',
            parent=self,
            suffix='mlt'
        ).create()

        mesh = msh.Mesh(
            root_name=root_name,
            parent=self,
            suffix='msh'
        ).create()

        poly_torus.plugs['output'].connect_to(mesh.plugs['inMesh'])
        multiply.plugs['input1X'].set_value(0.5)
        multiply.plugs['input1Y'].set_value(0.025)

        multiply.plugs['outputX'].connect_to(poly_torus.plugs['radius'])
        multiply.plugs['outputY'].connect_to(poly_torus.plugs['sectionRadius'])

        #self.plugs['size'].connect_to(multiply.plugs['input2X'])
        #self.plugs['size'].connect_to(multiply.plugs['input2Y'])

        poly_torus.plugs.set_values(
            subdivisionsAxis=16,
            subdivisionsHeight=8
        )

        self.nodes['mesh'] = mesh

        return self


class Sphere(hdl.Handle):

    default_data = dict()

    def __init__(self, *args, **kwargs):
        super(Sphere, self).__init__(*args, **kwargs)

    def create(self):

        super(Sphere, self).create()

        root_name = self.data['root_name']

        poly_sphere = dep.DependNode(
            root_name=root_name,
            node_type='polySphere',
            parent=self,
            suffix='psp'
        )

        multiply = dep.DependNode(
            root_name=root_name,
            node_type='multiplyDivide',
            parent=self,
            suffix='mlt'
        )

        mesh = msh.Mesh(
            root_name=root_name,
            parent=self,
            suffix='msh'
        )

        poly_sphere.plugs['output'].connect_to(mesh.plugs['inMesh'])
        multiply.plugs['input1X'].value = 0.75
        multiply.plugs['outputX'].connect_to(poly_sphere.plugs['radius'])
        #self.plugs['size'].connect_to(multiply.plugs['input2X'])

        poly_sphere.plugs.set_values(
            subdivisionsAxis=12,
            subdivisionsHeight=8
        )
        self.nodes['multiply_node'] = multiply
        self.nodes['mesh'] = mesh
        return self


class Cone(trn.Transform):

    default_data = dict(
        icon='cone',
        suffix='cone',
        aim_vector=nod.rig_settings['aim_vector'],
        height=2.0,
    )

    def __init__(self, *args, **kwargs):
        super(Cone, self).__init__(*args, **kwargs)

    def create(self):
        super(Cone, self).create()
        aim_vector = self.data['aim_vector']
        size = self.data['size']
        height = self.data['height']
        root_name = self.data['root_name']

        self.create_plug('shapeMatrix', type='matrix')

        #Add Compose matrix node and calculate transform geometry offset

        poly_cone = dep.DependNode(
            root_name=root_name,
            parent=self,
            suffix='pcn',
            node_type='polyCone'
        ).create()

        multiply = dep.DependNode(
            root_name=root_name,
            parent=self,
            suffix='mlt',
            node_type='multiplyDivide'
        ).create()

        mesh = msh.Mesh(
            root_name=root_name,
            parent=self
        ).create()

        transform_geometry = dep.DependNode(
            node_type='transformGeometry',
            root_name=root_name,
            parent=self,
            suffix='trg'
        ).create()

        poly_cone.plugs.set_values(
            subdivisionsAxis=10,
            axis=aim_vector,
            roundCap=1,
            subdivisionsCap=3,

        )

        mesh.plugs.set_values(
            overrideDisplayType=2,
            overrideEnabled=True
        )

        poly_cone.plugs['output'].connect_to(transform_geometry.plugs['inputGeometry'])
        transform_geometry.plugs['outputGeometry'].connect_to(mesh.plugs['inMesh'])
        #self.plugs['size'].connect_to(multiply.plugs['input1X'])
        #self.plugs['size'].connect_to(multiply.plugs['input1Y'])

        multiply.plugs['input2X'].value = 0.5
        multiply.plugs['input2Y'].value = height
        multiply.plugs['outputX'].connect_to(poly_cone.plugs['radius'])
        multiply.plugs['outputY'].connect_to(poly_cone.plugs['height'])

        shape_matrix = mtx.Matrix()
        shape_matrix.set_translate([x * height * size * 0.5 for x in aim_vector])

        self.nodes['mesh'] = mesh
        self.plugs['overrideEnabled'].value = True
        self.plugs['overrideRGBColors'].value = 1
        self.plugs['overrideColorRGB'].value = nod.rig_settings['alternate_rgb']

        self.plugs['shapeMatrix'].connect_to(transform_geometry.plugs['transform'])
        self.plugs['shapeMatrix'].value = shape_matrix.values

        return self


class SphereHandleArray(hay.HandleArray):

    default_data = dict(
        icon='handle_array',
        suffix='say'
    )

    def __init__(self, *args, **kwargs):
        super(SphereHandleArray, self).__init__(*args, **kwargs)
        self.node_constructor = Sphere

    def create(self):
        super(SphereHandleArray, self).create()
        self.nodes['items'][0].nodes['multiply_node'].plugs['input1X'].value = 1.0
        return self
