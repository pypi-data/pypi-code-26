# -*- coding: utf-8 -*-
from datetime import datetime


def datestr_to_dateobj(input_date_str):
    """
    convert a 'YYYY-MM-DD' date string to date object
    """
    return datetime.strptime(
        input_date_str, '%Y-%m-%d').date()
