import creaturecast_rigging.nodes.transform as trn
import creaturecast_rigging.nodes.depend_node as dep
import creaturecast_rigging.nodes.mesh as msh
import creaturecast_node.node as nod

rig_settings = nod.rig_settings


class Capsule(trn.Transform):

        default_data = dict(
                icon='capsule',
                suffix='cap',
                axis=rig_settings['aim_vector']
        )

        def __init__(self, *args, **kwargs):
                super(Capsule, self).__init__(*args, **kwargs)

        def create(self, **kwargs):
                super(Capsule, self).create()

                position_1_plug = self.create_plug('position1', type='double3', k=True)
                position_2_plug = self.create_plug('position2', type='double3', k=True)
                self.create_plug('size', dv=1.0)

                cylinder = dep.DependNode(
                        node_type='polyCylinder',
                        parent=self,
                        suffix='cyl'
                )

                mesh = msh.Mesh(
                        parent=self
                )

                multiply = dep.DependNode(
                        node_type='multiplyDivide',
                        parent=self,
                        suffix='mlt'
                )

                distance_node = dep.DependNode(
                        node_type='distanceBetween',
                        parent=self,
                        suffix='dst'
                )

                mesh.plugs['overrideEnabled'].set_value(True)
                mesh.plugs['overrideDisplayType'].set_value(2)

                cylinder.plugs['roundCap'].set_value(True)
                cylinder.plugs['subdivisionsCaps'].set_value(3)
                cylinder.plugs['subdivisionsAxis'].set_value(8)
                cylinder.plugs['axis'].set_value(rig_settings['aim_vector'])
                cylinder.plugs['output'].connect_to(mesh.plugs['inMesh'])
                position_1_plug.connect_to(distance_node.plugs['point1'])
                position_2_plug.connect_to(distance_node.plugs['point2'])
                distance_node.plugs['distance'].connect_to(cylinder.plugs['height'])
                self.plugs['size'].connect_to(multiply.plugs['input1X'])
                multiply.plugs['input2X'].set_value(0.5)
                multiply.plugs['outputX'].connect_to(cylinder.plugs['radius'])
                self.nodes['mesh'] = mesh
                self.nodes['cylinder'] = cylinder
                self.nodes['multiply'] = multiply
                self.nodes['distance_node'] = distance_node

                return self
