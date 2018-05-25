# coding=utf-8
"""
This code was generated by
\ / _    _  _|   _  _
 | (_)\/(_)(_|\/| |(/_  v1.0.0
      /       /
"""

from twilio.base.domain import Domain
from twilio.rest.trunking.v1 import V1


class Trunking(Domain):

    def __init__(self, twilio):
        """
        Initialize the Trunking Domain

        :returns: Domain for Trunking
        :rtype: twilio.rest.trunking.Trunking
        """
        super(Trunking, self).__init__(twilio)

        self.base_url = 'https://trunking.twilio.com'

        # Versions
        self._v1 = None

    @property
    def v1(self):
        """
        :returns: Version v1 of trunking
        :rtype: twilio.rest.trunking.v1.V1
        """
        if self._v1 is None:
            self._v1 = V1(self)
        return self._v1

    @property
    def trunks(self):
        """
        :rtype: twilio.rest.trunking.v1.trunk.TrunkList
        """
        return self.v1.trunks

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Trunking>'
