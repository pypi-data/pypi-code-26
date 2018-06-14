import creaturecast_rigging.rigging.transform_array as tay
import creaturecast_rigging.rigging.handle as hdl


class HandleArray(tay.TransformArray):

    default_data = dict(
        suffix='hry',
        icon='handle_array',
        item_data=dict(
            node_type='joint',
            shape='cube'
            )
        )

    node_constructor = hdl.Handle

    def __init__(self, *args, **kwargs):
        super(HandleArray, self).__init__(*args, **kwargs)

    def create(self):
        super(HandleArray, self).create()
        self.create_plug('size', dv=1.0)
        for handle in self.nodes['items']:
            self.plugs['size'].connect_to(handle.plugs['size'])

    def add_group(self):
        self.add_groups(1)

    def add_groups(self, count):
        groups = []
        for handle in self.nodes['items']:
            groups.extend(handle.add_groups(count))
        return groups

    def create_lengthy_handles(self):
        handles = self.nodes['items']
        for i, handle in enumerate(handles):
            if i != 0:
                handles[i-1].create_lengthy_handle(handles[i])

