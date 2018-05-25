# coding=utf-8
"""
This code was generated by
\ / _    _  _|   _  _
 | (_)\/(_)(_|\/| |(/_  v1.0.0
      /       /
"""

from twilio.base.domain import Domain
from twilio.rest.video.v1 import V1


class Video(Domain):

    def __init__(self, twilio):
        """
        Initialize the Video Domain

        :returns: Domain for Video
        :rtype: twilio.rest.video.Video
        """
        super(Video, self).__init__(twilio)

        self.base_url = 'https://video.twilio.com'

        # Versions
        self._v1 = None

    @property
    def v1(self):
        """
        :returns: Version v1 of video
        :rtype: twilio.rest.video.v1.V1
        """
        if self._v1 is None:
            self._v1 = V1(self)
        return self._v1

    @property
    def recordings(self):
        """
        :rtype: twilio.rest.video.v1.recording.RecordingList
        """
        return self.v1.recordings

    @property
    def compositions(self):
        """
        :rtype: twilio.rest.video.v1.composition.CompositionList
        """
        return self.v1.compositions

    @property
    def rooms(self):
        """
        :rtype: twilio.rest.video.v1.room.RoomList
        """
        return self.v1.rooms

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Video>'
