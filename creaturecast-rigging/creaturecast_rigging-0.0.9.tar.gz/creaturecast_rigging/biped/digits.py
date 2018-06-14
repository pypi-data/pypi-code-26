import copy

import creaturecast_rigging.biped.finger as fgr
import creaturecast_rigging.rigging.part_array as pay


def create_digits_template(amounts=[4, 5, 5, 5, 5], digit_name='finger', **kwargs):
        hand = DigitsTemplate(**kwargs).create()
        for i, count in enumerate(amounts):
            fgr.FingerTemplate(
                size=1.0,
                index=i+1,
                root_name=digit_name,
                parent=hand,
                count=count
            ).create()
        return hand


class DigitsTemplate(pay.PartArrayTemplate):

    default_data = copy.copy(pay.PartArrayTemplate.default_data)
    default_data.update(dict(
        icon='hand',
        root_name='digits',
        suffix='hnd',
    ))

    def __init__(self, *args, **kwargs):
        super(DigitsTemplate, self).__init__(*args, **kwargs)
        self.constructor = Digits


class Digits(pay.PartArray):

    default_data = copy.copy(pay.PartArray.default_data)
    default_data.update(dict(
        icon='hand',
        root_name='hand',
        suffix='hnd',
    ))

    def __init__(self, *args, **kwargs):
        super(Digits, self).__init__(*args, **kwargs)
        self.constructor = DigitsTemplate

    def create(self, **kwargs):
        super(Digits, self).create()

