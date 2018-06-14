import creaturecast_rigging.utilities as utl
import creaturecast_rigging.nodes.transform as trn
import creaturecast_rigging.nodes.nurbs_curve as ncv
import creaturecast_rigging.nodes.depend_node as dep
import creaturecast_rigging.rigging.handle_array as hry
import creaturecast_rigging.rigging.transform_array as tay
import creaturecast_rigging.rigging.constraint as cnt
import creaturecast_rigging.math.curve as mcv


def create_ribbon_handle_array(ribbon, **kwargs):
    if 'parent' not in kwargs:
        kwargs['parent'] = ribbon.parent
    array = RibbonHandleArray(**kwargs)
    array.nodes['ribbon'] = ribbon
    array.create()
    return array


class RibbonHandleArray(hry.HandleArray):

    default_data = dict(
        icon='muscle_grey',
        suffix='rhy',
        degree=2,
        form=0
    )

    def __init__(self, *args, **kwargs):

        super(RibbonHandleArray, self).__init__(*args, **kwargs)

    def create(self, **kwargs):
        super(RibbonHandleArray, self).create()
        ribbon = self.nodes['ribbon']
        size = self.data['size']
        side = self.data['side']
        root_name = self.data['root_name']
        count = self.data['count']
        degree = self.data['degree']
        spans = count-degree
        form = self.data['form']
        handles = self.nodes['items']
        #handle_groups = self.add_groups(1)

        position_array = tay.TransformArray(
            parent=self,
            root_name='%s_position' % root_name,
            count=count,
        )

        position_array.create()

        up_array = tay.TransformArray(
            parent=self,
            root_name='%s_up' % root_name,
            count=count
        ).create()

        curve_transform = trn.Transform(
            root_name='%s_curves' % root_name,
            parent=self,
        )

        surface_curve_a = ncv.NurbsCurve(
            root_name='%s_surface' % root_name,
            parent=curve_transform,
            index=1
        )

        surface_curve_b = ncv.NurbsCurve(
            root_name='%s_surface' % root_name,
            parent=curve_transform,
            index=2
        )

        surface_curve_iso_a = dep.DependNode(
            root_name=root_name,
            parent=self,
            index=1,
            node_type='curveFromSurfaceIso',
            suffix='cfs'
        )

        surface_curve_iso_b = dep.DependNode(
            root_name=root_name,
            parent=self,
            index=2,
            node_type='curveFromSurfaceIso',
            suffix='cfs'
        )

        curve_transform.plugs['visibility'].value = False
        surface_curve_iso_b.plugs['isoparmValue'].value = 1.0
        curve_transform.plugs['inheritsTransform'].value = False
        ribbon.plugs['worldSpace[0]'].connect_to(surface_curve_iso_a.plugs['inputSurface'])
        surface_curve_iso_a.plugs['outputCurve'].connect_to(surface_curve_a.plugs['create'])
        ribbon.plugs['worldSpace[0]'].connect_to(surface_curve_iso_b.plugs['inputSurface'])
        surface_curve_iso_b.plugs['outputCurve'].connect_to(surface_curve_b.plugs['create'])

        up_joints = up_array.nodes['items']
        position_joints = position_array.nodes['items']

        curve_positions = [x for x in mcv.plot_points(ribbon.data['positions'], count)]

        for i in range(count):
            parameter = 1.0 / (count - 1) * i

            # joint_array.parent_as_chain()

            point_on_curve = dep.DependNode(
                root_name=root_name,
                node_type='pointOnCurveInfo',
                suffix='poc',
                parent=position_joints[i]
            )

            point_on_curve_up = dep.DependNode(
                root_name='%s_up' % root_name,
                node_type='pointOnCurveInfo',
                suffix='poc',
                parent=position_joints[i]
            )

            surface_curve_a.plugs['worldSpace[0]'].connect_to(point_on_curve.plugs['inputCurve'])
            surface_curve_b.plugs['worldSpace[0]'].connect_to(point_on_curve_up.plugs['inputCurve'])

            point_on_curve.plugs['parameter'].value = parameter
            point_on_curve_up.plugs['parameter'].value = parameter
            point_on_curve.plugs['turnOnPercentage'].value = True
            point_on_curve_up.plugs['turnOnPercentage'].value = True

            position_joints[i].plugs['translate'].value = curve_positions[i].values
            up_joints[i].plugs['translate'].value = curve_positions[i].values

            up_joints[i].plugs['inheritsTransform'].value = False
            position_joints[i].plugs['inheritsTransform'].value = False

            point_on_curve_up.plugs['position'].connect_to(up_joints[i].plugs['translate'])
            point_on_curve.plugs['position'].connect_to(position_joints[i].plugs['translate'])

            if i > 0:
                cnt.create_tangent_constraint(
                    surface_curve_a,
                    position_joints[i-1],
                    world_up_object=handles[-1],
                    worldUpType='object',
                    aimVector=utl.get_side_aim_vector(side),
                    upVector=utl.get_side_up_vector(side)
                )

            cnt.create_parent_constraint(
                position_joints[i],
                handles[i],
                mo=False
            )
