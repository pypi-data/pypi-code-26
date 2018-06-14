import copy

import rigging.ribbon_chain as rcn
import creaturecast_core.math.matrix as mtx
import creaturecast_rigging.rigging.handle_array as hay
import creaturecast_rigging.rigging.handle as hdl
import creaturecast_rigging.rigging.constraint as cnt


class NeckTemplate(rcn.RibbonChainTemplate):


    default_data = copy.copy(rcn.RibbonChainTemplate.default_data)
    default_data.update(dict(
        icon='neck',
        root_name='neck',
        suffix='nck',
        count=4,
        sub_structure=[4, 7]
    ))

    def __init__(self, *args, **kwargs):
        super(NeckTemplate, self).__init__(*args, **kwargs)
        self.constructor = Neck

    def create(self):
        super(NeckTemplate, self).create()

        return self


class Neck(rcn.RibbonChain):

    default_data = copy.copy(rcn.RibbonChain.default_data)
    default_data.update(dict(
        icon='neck',
        root_name='neck',
        suffix='nck',
        parent_as_chain=False
    ))

    def __init__(self, *args, **kwargs):
        super(Neck, self).__init__(*args, **kwargs)
        self.constructor = NeckTemplate

    def create(self, **kwargs):
        super(Neck, self).create()

        side = self.data['side']

        handle_arrays = self.get_nodes('handle_arrays')
        handle_array = handle_arrays[0]
        handles = handle_array.get_nodes('items')
        sub_handle_array = handle_arrays[1]
        sub_handles = sub_handle_array.get_nodes('items')
        joints = self.get_nodes('joints')
        fk_handles = self.get_nodes('fk_handles')


        handle_array.create_lengthy_handles()

        sub_handles[-1].plugs['visibility'].set_value(False)
        handles[-1].plugs['visibility'].set_value(False)

        handle_array.parent_as_chain()

        side_dictionary = {0: 0, 1: 1, -1: 2, 2: 0}
        joints[0].plugs['type'].set_value(1)
        joints[0].plugs['side'].set_value(side_dictionary[side])

        for joint in joints[1:]:
            joint.plugs['type'].set_value(7)
            joint.plugs['side'].set_value(side_dictionary[side])

        joints[-2].plugs['type'].set_value(8)
        joints[-1].plugs['type'].set_value(0)

        for handle in fk_handles:
            handle.plugs['rotateOrder'].set_value(1)

        return self


    def create_human_ik_skeleton(self, parent=None):
        super(Neck, self).create_human_ik_skeleton()

        side = self.data['side']
        size = self.data['size']

        fk_handles = self.get_nodes('fk_handles')
        new_joints = []
        for i, handle in enumerate(fk_handles):

            new_joint = hdl.Handle(
                root_name='%s_human_ik' % handle.data['root_name'],
                index=handle.data['index'],
                side=handle.data['side'],
                size=size*0.1,
                matrix=handle.matrix.values,
                shape='cube',
                node_type='joint'
            ).create()
            new_joint.plugs['drawStyle'].set_value(2)

            side_dictionary = {0: 0, 1: 1, -1: 2, 2: 0}

            cnt.ParentConstraint(
                parent=parent,
                build_kwargs={'mo': False}
            ).create(
                new_joint,
                handle
            )
            if i != 0:
                new_joint.set_parent(new_joints[-1])
                new_joint.plugs['side'].set_value(side_dictionary[side])
                new_joints[i - 1].create_lengthy_handle(new_joint)

            else:
                new_joint.plugs['side'].set_value(side_dictionary[side])

            if i == len(fk_handles)-1:
                new_joint.plugs['type'].set_value(8)
            else:
                new_joint.plugs['type'].set_value(7)

            new_joints.append(new_joint)

        if parent:
            new_joints[0].set_parent(parent)

        return new_joints
