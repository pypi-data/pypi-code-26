# -*- coding: utf-8 -*-

"""Top-level package for Stripe testing."""

__author__ = """Ben Lopatin"""
__email__ = 'ben@benlopatin.com'
__version__ = '0.1.0'

from datetime import date


class Card(object):
    """
    Represents a credit card with number &c.
    """
    def __init__(self, number=None, expiry=None, cvc=None):
        self.number = number or "4242424242424242"
        self.expiry = expiry or date.today().replace(year=date.today().year + 1)
        self.cvc = cvc or 123

    def data(self, number=None, expiry_month=None, expiry_year=None, cvc=None):
        return {
            "number": number or self.number,
            "expire_month": expiry_month or self.expiry.month,
            "expire_year": expiry_year or self.expiry.year,
            "cvc": cvc or self.cvc,
        }
    valid = data

    def attach_and_fail_charge(self):
        """
        Attaching this card to a Customer object succeeds, but attempts to charge the customer fail.
        """
        return self.data(number="4000000000000341")


class Visa(Card):
    """A Visa card"""

