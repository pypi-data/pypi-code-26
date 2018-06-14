import copy

import creaturecast_rigging.rigging.fk_chain as fkc


class ShoulderTemplate(fkc.FkChainTemplate):

    default_data = copy.copy(fkc.FkChainTemplate.default_data)
    default_data.update(dict(
        icon='bone',
        root_name='shoulder',
        suffix='sdr',
    ))

    def __init__(self, *args, **kwargs):
        kwargs['count'] = 2
        super(ShoulderTemplate, self).__init__(*args, **kwargs)
        self.constructor = Shoulder


class Shoulder(fkc.FkChain):

    default_data = copy.copy(fkc.FkChain.default_data)
    default_data.update(dict(
        icon='bone',
        root_name='shoulder',
        suffix='sdr',
    ))

    def __init__(self, *args, **kwargs):
        super(Shoulder, self).__init__(*args, **kwargs)
        self.constructor = ShoulderTemplate
