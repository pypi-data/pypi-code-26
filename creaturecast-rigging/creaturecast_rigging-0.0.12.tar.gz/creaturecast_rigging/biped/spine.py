import creaturecast_rigging.rigging.ribbon_chain as rcn
import creaturecast_rigging.math.matrix as mtx
import creaturecast_rigging.rigging.handle_array as hay
import creaturecast_rigging.rigging.constraint as cnt
import creaturecast_rigging.rigging.handle as hdl


class SpineTemplate(rcn.RibbonChainTemplate):

    default_data = dict(
        icon='/images/icons/spine.png',
        root_name='spine',
        suffix='spn',
        count=4,
        side=2,
        sub_structure=[4, 7]
    )

    def __init__(self, *args, **kwargs):
        super(SpineTemplate, self).__init__(*args, **kwargs)
        self.constructor = Spine

    def create(self):
        super(SpineTemplate, self).create()
        return self


class Spine(rcn.RibbonChain):

    default_data = dict(
        icon='spine',
        root_name='spine',
        suffix='spn',
        parent_as_chain=False,
        sub_structure=[4, 7]
    )

    def __init__(self, *args, **kwargs):
        super(Spine, self).__init__(*args, **kwargs)
        self.constructor = SpineTemplate

    def create(self, **kwargs):
        super(Spine, self).create()
        size = self.data['size']
        side = self.data['side']
        root_count = 1
        root_name = self.data['root_name']
        joints = list(self.nodes['joints'])
        handles = list(self.nodes['handles'])
        handle_arrays = self.nodes['handle_arrays']

        handle_arrays = self.nodes['handle_arrays']
        main_sub_handles = handle_arrays[0].nodes['items']

        root_handle_array = hay.HandleArray(
                root_name='%s_root' % root_name,
                parent=self,
                size=size*2.0,
                count=root_count,
                item_data=dict(
                    shape='circle',
                    groups=1
                )
        ).create()

        root_matrix = mtx.Matrix()
        root_matrix.set_translate(handles[0].matrix.get_translate())
        root_handle_array.matrix = root_matrix

        root_handle_array.parent_as_chain(reverse=True)
        root_handles = root_handle_array.nodes['items']
        handles.extend(root_handles)

        handle_arrays[0].set_parent(root_handles[0])

        handle_arrays[0].create_lengthy_handles()

        for handle_array in handle_arrays:
            handle_array.nodes['items'][-1].plugs['visibility'].value = False

        cnt.create_parent_constraint(
            main_sub_handles[-1],
            main_sub_handles[-2],
            mo=True,
        )

        side_dictionary = {0: 0, 1: 1, -1: 2, 2: 0}
        joints[0].plugs['type'].set_value(1)
        joints[0].plugs['side'].set_value(side_dictionary[side])

        for joint in joints[1:]:
            joint.plugs['type'].set_value(6)
            joint.plugs['side'].set_value(side_dictionary[side])

        if self.data.get('worldSpace', False):
            for h in handles:
                h.plugs['rotateOrder'].value = 2

        self.nodes['handles'] = handles
        self.nodes['joints'] = joints
        self.nodes['handles'] = handles
        self.nodes['root_handle_array'] = root_handle_array

        return self

    def create_human_ik_skeleton(self, parent=None):

        super(Spine, self).create_human_ik_skeleton()

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
                new_joint.plugs['type'].set_value(6)
                new_joint.plugs['side'].set_value(side_dictionary[side])
                new_joints[i-1].create_lengthy_handle(new_joint)

            else:
                new_joint.plugs['type'].set_value(1)
                new_joint.plugs['side'].set_value(side_dictionary[side])

            new_joints.append(new_joint)

        if parent:
            new_joints[0].set_parent(parent)

        return new_joints


