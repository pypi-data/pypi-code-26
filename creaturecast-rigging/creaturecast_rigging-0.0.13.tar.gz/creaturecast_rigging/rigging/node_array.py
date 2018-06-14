import copy
import creaturecast_node.node as nod
import creaturecast_rigging.utilities as mut


class NodeArray(nod.Node):

    default_data = dict(
        count=5
    )

    default_item_data = dict()

    node_constructor = nod.Node

    def __init__(self, *args, **kwargs):
        super(NodeArray, self).__init__(*args, **kwargs)
        self.current = 0

    def create(self):
        super(NodeArray, self).create()
        count = self.data['count']
        side = self.data['side']
        size = self.data['size']
        index_name = self.get_index_name()

        symmetry_data = mut.create_symmetry_data(count, side, size)

        items = []
        for i in range(count):
            item_data = copy.copy(self.data['item_data'])
            item_data.update(
                parent=self,
                index=symmetry_data['indices'][i],
                side=symmetry_data['sides'][i],
                root_name=index_name
            )
            new_item = self.node_constructor(**item_data)
             #if issubclass(new_item, trn.Transform):
             #   new_item.set_translate(symmetry_data['positions'][i])
            new_item.create()
            items.append(new_item)
        self.nodes['items'] = items
        return self

    def __iter__(self):
        for item in self.nodes['items']:
            yield item

    def next(self):
        items = self.nodes['items']
        if self.current > len(items):
            raise StopIteration
        else:
            self.current += 1
            return self.current - 1
