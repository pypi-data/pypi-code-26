import copy

import rigging.fk_chain as fkc
import copy
import rigging.fk_chain as fkc
import creaturecast_rigging.rigging.shader as shd
import creaturecast_node.node as nod
import rigging.template as tpt
import creaturecast_rigging.rigging.constraint as cnt
import creaturecast_rigging.rigging.part as prt

class FingerTemplate(fkc.FkChainTemplate):

    default_data = copy.copy(fkc.FkChainTemplate.default_data)
    default_data.update(dict(
        icon='digit',
        root_name='finger',
        suffix='fgr',
        count=5,
    ))

    def __init__(self, *args, **kwargs):
        super(FingerTemplate, self).__init__(*args, **kwargs)
        self.constructor = Finger


class Finger(fkc.FkChain):

    default_data = copy.copy(fkc.FkChain.default_data)
    default_data.update(dict(
        icon='digit',
        root_name='finger',
        suffix='fgr',
        count=5,
    ))

    def __init__(self, *args, **kwargs):
        super(Finger, self).__init__(*args, **kwargs)
        self.constructor = FingerTemplate

    def create(self, **kwargs):
        super(Finger, self).create()
        size = self.data['size']
        count = self.data['count']
