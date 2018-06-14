import creaturecast_rigging.math.matrix as mtx
import creaturecast_rigging.rigging.node_array as nry
import creaturecast_rigging.nodes.transform as trn


class TransformArray(trn.Transform, nry.NodeArray):

    default_data = dict(
        suffix='try',
        parent_as_chain=False,
        matrices=[],
        count=0,
        item_data=dict()
    )
    node_constructor = trn.Transform

    def __init__(self, *args, **kwargs):
        self.matrices = []

        if 'matrices' in kwargs:
            self.matrices = [mtx.Matrix(x) for x in kwargs.pop('matrices', [])]
            kwargs['count'] = len(self.matrices)
        elif 'count' in kwargs:
            for i in range(kwargs['count']):
                self.matrices.append(mtx.Matrix())
        else:
            raise Exception('Must specify matrices or count to create %s' % self.__class__.__name__)

        super(TransformArray, self).__init__(*args, **kwargs)

    def create(self):
        super(TransformArray, self).create()
        if self.data['parent_as_chain']:
            self.parent_as_chain()
        if self.matrices:
            items = self.nodes['items']
            for i, matrix in enumerate(self.matrices):
                items[i].matrix = matrix

        return self

    def parent_as_chain(self, reverse=False):
        transforms = self.nodes['items']
        for itr in range(len(transforms)):
            if itr != 0:
                if reverse:
                    transforms[itr-1].set_parent(transforms[itr])
                else:
                    transforms[itr].set_parent(transforms[itr-1])
