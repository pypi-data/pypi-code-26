"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.utils.crypto import PubCrypto
from pubkeeper.patron.patron import Patron
from binascii import unhexlify
from pubkeeper.protocol.v1.frame import Frame


class ProtocolPatron(Patron):
    def configure(self):
        self._uses_crypto = self._kwargs.pop('crypto', True)

    def new_brewers(self, brewers):
        with self.topic_lock:
            # Need to load all brewers first, before starting patrons
            # this prevents potential race conditions when using a shared
            # brew resource, the first may acquire a LVC, before crypto
            # keys for the latter are stored
            for brewer in brewers:
                brew = self.get_brew(brewer['brew']['name'])

                if brew is None:
                    raise RuntimeError("Patron could not match a parity "
                                       "brew for brewer brew: {}".format(
                                           brewer['brew']
                                       ))

                if brewer['brewer_id'] in self._patroning:
                    self.remove_brewer(brewer['brewer_id'])

                self._patroning[brewer['brewer_id']] = {
                    'topic': brewer['topic'],
                    'brew': brew,
                    'config': brewer['brewer_config']
                }

            for brewer in brewers:
                # We don't want to use self.topic here as it may be a
                # wild card, and our brew may depend on the literal topic
                # of information.
                brew = self.get_brew(brewer['brew']['name'])
                brew.start_patron(self.patron_id,
                                  brewer['topic'],
                                  brewer['brewer_id'],
                                  brewer['brewer_config'],
                                  brewer['brew'],
                                  self._handle_callback)

                self.logger.info("Started patron for {}:{}".format(
                    brewer['topic'], brewer['brewer_id']
                ))

    def remove_brewer(self, brewer_id):
        with self.topic_lock:
            if brewer_id in self._patroning:
                patron = self._patroning[brewer_id]

                patron['brew'].stop_patron(self.patron_id,
                                           patron['topic'],
                                           brewer_id)

                del(self._patroning[brewer_id])

                self.logger.info("Stopped patron for {}:{}".format(
                    patron['topic'], brewer_id
                ))

    def reset(self):
        with self.topic_lock:
            for brewer_id in self._patroning.keys():
                self.remove_brewer(brewer_id)

    def _handle_callback(self, brewer_id, data):
        with self.topic_lock:
            if brewer_id not in self._patroning:  # pragma no cover
                self.logger.debug("Patron: {} is not patronizing brewer: {}".
                                  format(self.patron_id, brewer_id))
                return

            try:
                (topic_hash, sender_brewer_id, data) = Frame.unpack(data)
            except ValueError:
                self.logger.exception("Unable to parse incoming data packet")
                return
            except:  # noqa - If anything happens while unpacking, do not die.
                self.logger.exception("Unable to parse incoming data packet")
                return

            # double check making sure data came from intended brewer id
            if sender_brewer_id != brewer_id:  # pragma no cover
                self.logger.debug(
                    "Patron:{} discarding data from "
                    "brewer:{}, brewer accepted:{}".
                    format(self.patron_id, sender_brewer_id, brewer_id))
                return
            brewer_config = self._patroning[brewer_id]['config']

        if self._uses_crypto and 'cipher' in brewer_config:
            try:
                if brewer_id not in self._ciphers:
                    self._ciphers[brewer_id] = PubCrypto(
                        brewer_config['cipher']['mode'],
                    )

                cipher = self._ciphers[brewer_id]
                self._callback(cipher.decrypt(
                    unhexlify(brewer_config['cipher']['key'].encode()),
                    data
                ))
            except Exception:
                self.logger.exception("Unable to decrypt data")
        else:
            self._callback(data)
