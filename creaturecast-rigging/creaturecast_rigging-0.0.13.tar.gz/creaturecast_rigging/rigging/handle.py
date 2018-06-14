import creaturecast_node.node as nod
import creaturecast_rigging.nodes.joint as jnt
import creaturecast_rigging.math.matrix as mtx
import creaturecast_rigging.nodes.nurbs_curve as ncv
import creaturecast_rigging.nodes.depend_node as dep
import creaturecast_rigging.nodes.transform as trn
import copy
handle_shapes = nod.handle_shapes


class Handle(jnt.Joint):

    default_data = dict(
        shape=None,
        suffix='hdl',
        icon='handle'
    )

    """
    A transform with visible child geometry (usually nurbs) intended for user input.
    Default for keyword arguments are as follows:
    """

    def __init__(self, *args, **kwargs):
        super(Handle, self).__init__(*args, **kwargs)
        self.shape_matrix = mtx.Matrix()
        self.shape_matrix.set_scale([self.data['size']]*3)
        self.shapes = []

    def create(self):
        super(Handle, self).create()
        matrix_plug = self.create_plug('shapeMatrix', type='matrix')
        self.create_plug('size', dv=1.0)

        self.nodes['curves'] = []
        self.nodes['base_curves'] = []
        self.nodes['transform_geometries'] = []
        shape = self.data.get('shape', [])
        if shape is not None:
            for i, shape_data in enumerate(handle_shapes[shape]):
                side = self.data['side']
                index_name = self.data['root_name']

                curve = ncv.NurbsCurve(
                        root_name=index_name,
                        index=i+1,
                        side=side,
                        parent=self
                )

                base_curve_data = copy.copy(curve.data)
                base_curve_data.update(shape_data)
                base_curve_data.update(dict(
                    root_name='base_%s' % index_name,
                    parent=self
                ))

                base_curve = ncv.NurbsCurve(**base_curve_data)

                transform_geometry = dep.DependNode(
                        root_name=index_name,
                        index=i+1,
                        side=side,
                        node_type='transformGeometry',
                        suffix='tgm',
                        parent=self
                )

                matrix_plug.connect_to(transform_geometry.plugs['transform'])
                matrix_plug.set_value(self.shape_matrix.values)
                base_curve.plugs['worldSpace'].connect_to(transform_geometry.plugs['inputGeometry'])
                transform_geometry.plugs['outputGeometry'].connect_to(curve.plugs['create'])

                base_curve.plugs['intermediateObject'].set_value(True)

                self.nodes['curves'].append(curve)
                self.nodes['base_curves'].append(base_curve)
                self.nodes['transform_geometries'].append(transform_geometry)
        return self

    def create_lengthy_handle(self, *args):
        pass

    def add_group(self):
        return self.add_groups(1)[0]

    def add_groups(self, count):
        top_node = self
        groups = self.nodes.get('groups', [])
        if groups:
            top_node = groups[0]
        index_name = self.get_index_name()
        parent = top_node.parent
        new_groups = []
        for i in range(count):
            group = trn.Transform(
                root_name=index_name,
                index=i,
                side=self.data['side'],
                parent=parent,
                matrix=self.matrix
            )
            parent = group
            new_groups.append(group)
        new_groups.extend(groups)
        self.set_parent(new_groups[-1])
        self.nodes['groups'] = new_groups
        return new_groups
