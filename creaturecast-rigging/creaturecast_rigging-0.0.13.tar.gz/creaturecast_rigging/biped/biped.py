import creaturecast_rigging.rigging.body as bod
import creaturecast_rigging.rigging.skeleton as skl
import creaturecast_rigging.rigging.part as prt
import creaturecast_rigging.rigging as rig
import creaturecast_rigging.biped.arm as arm
import creaturecast_rigging.biped.spine as spn


class BipedTemplate(bod.BodyTemplate):
    default_data = dict(
        icon='/images/icons/man.png',
        root_name='body',
        suffix='bpd',
        human_ik_skeleton=False
    )

    def __init__(self, *args, **kwargs):
        super(BipedTemplate, self).__init__(*args, **kwargs)
        self.constructor = Biped

    def create(self):
        super(BipedTemplate, self).create()
        '''
        self.data['pretty_name'] = 'Biped(Generic)'

        spine = spn.SpineTemplate(
            parent=self,
            size=4.0,
            side=2,
            root_name='spine',
            pretty_name='Spine',
            sub_structure=(7, 22),
            matrices=[
                [0.0, 0.0, 0.0],
                [0.0, 10.0, 3.0],
                [0.0, 20.0, 0.0],
                [0.0, 25.0, 0.0],
                [0.0, 10.0, -20.0]
            ]
        )
        spine.create()


        left_arm = arm.ArmTemplate(
            parent=self,
            root_name='arm',
            pretty_name='Arm (Left)',
            side=0,
            matrices=[
                [2.0, 20.0, 0.0],
                [5.0, 20.0, 0.0],
                [15.0, 20.0, -5.0],
                [25.0, 20.0, 0.0],
                [30.0, 20.0, 0.0],
                [2.0, 20.0, -20.0],
                [15.0, 20.0, -20.0],
                [25.0, 20.0, -20.0]
            ]
        )

        left_arm.create()

        right_arm = arm.ArmTemplate(
            parent=self,
            root_name='arm',
            pretty_name='Arm (Right)',
            side=1,
            matrices=[
                [-2.0, 20.0, 0.0],
                [-5.0, 20.0, 0.0],
                [-15.0, 20.0, -5.0],
                [-25.0, 20.0, 0.0],
                [-30.0, 20.0, 0.0],
                [-2.0, 20.0, -20.0],
                [-15.0, 20.0, -20.0],
                [-25.0, 20.0, -20.0]
            ]
        )
        right_arm.create()

        self.nodes['parts'] = [spine, left_arm, right_arm]

        self.assign_part_shaders()
        '''


class Biped(bod.Body):
    default_data = dict(
        icon='man',
        root_name='body',
        suffix='bpd'
    )

    def __init__(self, *args, **kwargs):
        super(Biped, self).__init__(*args, **kwargs)
        self.constructor = BipedTemplate

    def create_human_ik_skeleton(self, parent=None):
        root_name = self.data['root_name']
        joint_size = self.data['size'] * 0.02

        skeleton = skl.Skeleton(
            side=self.data['side'],
            size=joint_size,
            index=self.data['index'],
            root_name='%s_human_ik' % root_name
        ).create()

        skeleton.plugs['overrideEnabled'].set_value(True)
        skeleton.plugs['overrideRGBColors'].set_value(1)
        skeleton.plugs['overrideColorRGB'].set_value(rig.settings['human_ik_color'])

        for part in self.get_children(node_type=prt.Part):
            part.create_human_ik_skeleton(parent=skeleton)

        if parent:
            skeleton.set_parent(parent)

        return skeleton
