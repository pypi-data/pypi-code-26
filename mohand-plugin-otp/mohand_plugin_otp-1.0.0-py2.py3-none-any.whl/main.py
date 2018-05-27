# encoding=utf8
from __future__ import unicode_literals

from mohand import hands
from mohand_plugin_otp.hand import otp
from mohand_plugin_otp.version import get_setup_version


class OtpHand(hands.HandBase):
    '''用以提供定制化的一次性密码生成服务'''

    def register(self):
        return otp

    def version(self):
        return 'mohand-plugin-otp', get_setup_version()
