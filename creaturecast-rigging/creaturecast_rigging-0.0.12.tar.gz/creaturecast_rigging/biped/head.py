import copy

import rigging.fk_chain as fkc
import creaturecast_rigging.rigging.shader as shd
import creaturecast_node.node as nod
import rigging.template as tpt
import creaturecast_rigging.rigging.constraint as cnt
import creaturecast_rigging.rigging.part as prt

class HeadTemplate(fkc.FkChainTemplate):

    default_data = copy.copy(fkc.FkChainTemplate.default_data)
    default_data.update(dict(
        icon='skull',
        root_name='head',
        suffix='hed',
    ))

    def __init__(self, *args, **kwargs):
        kwargs['count'] = 2
        super(HeadTemplate, self).__init__(*args, **kwargs)
        self.constructor = Head

class Head(fkc.FkChain):

    default_data = copy.copy(fkc.FkChain.default_data)
    default_data.update(dict(
        icon='skull',
        root_name='head',
        suffix='hed',
    ))

    def __init__(self, *args, **kwargs):
        super(Head, self).__init__(*args, **kwargs)
        self.constructor = HeadTemplate

    def create(self, **kwargs):
        super(Head, self).create()
        size = self.data['size']
        count = self.data['count']
