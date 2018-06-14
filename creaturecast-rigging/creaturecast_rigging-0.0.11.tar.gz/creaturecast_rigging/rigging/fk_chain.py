import creaturecast_rigging.rigging.constraint as cnt
import creaturecast_rigging.rigging.template as tpt
import creaturecast_rigging.rigging.handle_array as hry
import creaturecast_rigging.rigging.joint_array as jry
import creaturecast_rigging.rigging.part as prt


class FkChainTemplate(tpt.UpChainTemplate):

    default_data = dict(
        icon='/images/icons/chain.png',
        suffix='fkc',
    )

    def __init__(self, *args, **kwargs):
        super(FkChainTemplate, self).__init__(
            *args,
            **kwargs
        )
        self.constructor = FkChain

class FkChain(prt.Part):

    default_data = dict(
        icon='/images/icons/chain.png',
        root_name='template_chain',
        suffix='fkc',
    )

    def __init__(self, *args, **kwargs):
        super(FkChain, self).__init__(*args, **kwargs)
        self.constructor = FkChainTemplate

    def create(self, **kwargs):
        super(FkChain, self).create()
        size = self.data['size']
        matrices = self.matrices

        handle_array = hry.HandleArray(
                parent=self,
                matrices=matrices,
                parent_as_chain=True,
                item_data=dict(
                    node_type='transform',
                    shape='cube',
                )
        ).create()

        handle_array.create_lengthy_handles()
        handle_array.add_groups(1)

        joint_array = jry.JointArray(
                parent=self,
                matrices=matrices,
                parent_as_chain=True,
                size=size*0.25
        ).create()

        handles = handle_array.nodes['items']
        base_joints = joint_array.nodes['items']

        handles[-1].plugs['visibility'].value = False

        for i, handle in enumerate(handles):

            cnt.create_parent_constraint(
                handles[i],
                base_joints[i],
                mo=False
            )

        self.nodes['base_joints'] = base_joints
        self.nodes['handle_array'] = handle_array
        self.nodes['joint_array'] = joint_array
        self.nodes['joints'] = base_joints
        self.nodes['handles'] = handles

        return self
