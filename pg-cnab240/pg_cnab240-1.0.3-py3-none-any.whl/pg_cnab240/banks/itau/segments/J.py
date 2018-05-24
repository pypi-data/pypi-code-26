from datetime import datetime
from pg_cnab240.segment_section import SegmentSection
from pg_cnab240.banks.itau.segments.headers.slip_header import SlipHeader
from pg_cnab240.banks.itau.segments.footers.slip_footer import SlipFooter


class SegmentJ(SegmentSection):
    def __init__(self, data=None):
        super().__init__('SegmentJ', data, {
            'bank_code': {
                'type': 'int',
                'length': 3,
                'default': 341,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': True,
                'start': 0,
                'end': 3,
                'value': None,
            },
            'lot_code': {
                'type': 'int',
                'length': 4,
                'default': 0000,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': False,
                'start': 3,
                'end': 7,
                'value': None,
            },
            'register_type': {
                'type': 'int',
                'length': 1,
                'default': 3,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': False,
                'start': 7,
                'end': 8,
                'value': None,
            },
            'register_number': {
                'type': 'int',
                'length': 5,
                'default': 0,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': True,
                'start': 8,
                'end': 13,
                'value': None,
            },
            'segment': {
                'type': 'string',
                'length': 1,
                'default': 'J',
                'pad_content': ' ',
                'pad_direction': 'left',
                'required': False,
                'start': 13,
                'end': 14,
                'value': None,
            },
            'move_type': {
                'type': 'int',
                'length': 3,
                'default': 0,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': True,
                'start': 14,
                'end': 17,
                'value': None,
            },
            'favored_bank': {
                'type': 'int',
                'length': 3,
                'default': 0,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': True,
                'start': 17,
                'end': 20,
                'value': None,
            },
            'currency_type': {
                'type': 'int',
                'length': 1,
                'default': 9,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': True,
                'start': 20,
                'end': 21,
                'value': None,
            },
            'dv': {
                'type': 'int',
                'length': 1,
                'default': 0,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': True,
                'start': 21,
                'end': 22,
                'value': None,
            },
            'due_rule': {
                'type': 'int',
                'length': 4,
                'default': 0,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': True,
                'start': 22,
                'end': 26,
                'value': None,
            },
            'amount': {
                'type': 'float',
                'length': 10,
                'default': 0,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': True,
                'start': 26,
                'end': 36,
                'value': None,
            },
            'free_field': {
                'type': 'int',
                'length': 25,
                'default': 0,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': True,
                'start': 36,
                'end': 61,
                'value': None,
            },
            'favored_name': {
                'type': 'string',
                'length': 30,
                'default': '',
                'pad_content': ' ',
                'pad_direction': 'right',
                'required': True,
                'start': 62,
                'end': 91,
                'value': None,
            },
            'due_date': {
                'type': 'date',
                'length': 8,
                'default': 0,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': True,
                'start': 91,
                'end': 99,
                'value': None,
            },
            'title_amount': {
                'type': 'float',
                'length': 15,
                'default': 0,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': True,
                'start': 99,
                'end': 114,
                'value': None,
            },
            'discounts': {
                'type': 'float',
                'length': 15,
                'default': 0,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': False,
                'start': 114,
                'end': 129,
                'value': None,
            },
            'additions': { # forfeit + interest amounts
                'type': 'float',
                'length': 15,
                'default': 0,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': False,
                'start': 129,
                'end': 144,
                'value': None,
            },
            'pay_date': {
                'type': 'date',
                'length': 8,
                'default': 0,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': True,
                'start': 144,
                'end': 152,
                'value': None,
            },
            'payment_amount': {
                'type': 'float',
                'length': 15,
                'default': 0,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': True,
                'start': 152,
                'end': 167,
                'value': None,
            },
            'payment_zeros': {
                'type': 'zeros',
                'length': 15,
                'default': 0,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': False,
                'start': 167,
                'end': 182,
                'value': None,
            },
            'your_number': {
                'type': 'string',
                'length': 20,
                'default': '',
                'pad_content': ' ',
                'pad_direction': 'right',
                'required': True,
                'start': 182,
                'end': 202,
                'value': None,
            },
            'your_number_whites': {
                'type': 'whites',
                'length': 13,
                'default': '',
                'pad_content': ' ',
                'pad_direction': 'right',
                'required': False,
                'start': 202,
                'end': 215,
                'value': None,
            },
            'our_number': {
                'type': 'string',
                'length': 15,
                'default': ' ',
                'pad_content': ' ',
                'pad_direction': 'right',
                'required': False,
                'start': 215,
                'end': 230,
                'value': None,
            },
            'occurrences': {
                'type': 'string',
                'length': 10,
                'default': '',
                'pad_content': ' ',
                'pad_direction': 'right',
                'required': False,
                'start': 230,
                'end': 240,
                'value': None,
            },
        }, SlipHeader, SlipFooter)
