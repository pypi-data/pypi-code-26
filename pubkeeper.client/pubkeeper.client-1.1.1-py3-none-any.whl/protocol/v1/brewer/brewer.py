"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.brewer import Brewer
from pubkeeper.utils.crypto import PubCrypto
from Crypto import Random
from Crypto.Cipher import AES
from binascii import hexlify, unhexlify
from pubkeeper.protocol.v1.frame import Frame


class ProtocolBrewer(Brewer):
    def configure(self):
        self._uses_crypto = self._kwargs.pop('crypto', True)
        self._crypto = None
        self._cipher = None

        if self._uses_crypto:
            self._crypto = {
                'mode': AES.MODE_CBC,
                'key': hexlify(Random.new().read(16)).decode()
            }
            self._cipher = PubCrypto(
                self._crypto['mode']
            )

    def get_config(self):
        ret = {}

        if hasattr(self, '_uses_crypto') and self._uses_crypto:
            ret['cipher'] = self._crypto

        return ret

    def new_patrons(self, patrons):
        with self.topic_lock:
            for patron in patrons:
                brew = self.get_brew(patron['brew']['name'])

                if brew is None:
                    raise RuntimeError("Brewer could not match a parity "
                                       "brew for patron brew: {}".format(
                                           patron['brew']
                                       ))

                if brew in self._brewing and \
                        patron['patron_id'] in self._brewing[brew]:
                    self.remove_patron(patron['patron_id'])

                if brew not in self._brewing:
                    self._brewing[brew] = {
                        patron['patron_id']: patron['brew']
                    }
                else:
                    self._brewing[brew][patron['patron_id']] = patron['brew']

            for patron in patrons:
                brew.start_brewer(self.brewer_id,
                                  self.topic,
                                  patron['patron_id'],
                                  patron['brew'])

                self.logger.info("Started brewer for {}:{}".format(
                    self.topic, patron['patron_id']
                ))

    def remove_patron(self, patron_id, everyone=False):
        with self.topic_lock:
            for brew, patrons in self._brewing.copy().items():
                if patron_id in patrons or everyone:
                    brew.stop_brewer(self.brewer_id,
                                     self.topic,
                                     patron_id)

                    del(self._brewing[brew][patron_id])

                if len(self._brewing[brew]) == 0:
                    del(self._brewing[brew])

                self.logger.info("Stopped brewer for {}:{}".format(
                    self.topic, patron_id
                ))

    def reset(self):
        with self.topic_lock:
            self.remove_patron(None, True)

    def brew(self, data):
        if hasattr(self, '_uses_crypto') and self._uses_crypto:
            data = self._cipher.encrypt(
                unhexlify(self._crypto['key']),
                data
            )

        self.logger.debug(
            "Brewer id: {} brewing on topic: {}, on {} brews".
            format(self.brewer_id, self.topic, len(self._brewing)))

        frame = Frame.pack(self.topic, self.brewer_id, data)
        with self.topic_lock:
            for brew, patrons in self._brewing.items():
                self._io_loop.add_callback(
                    brew.brew,
                    self.brewer_id,
                    self.topic,
                    frame,
                    patrons)
