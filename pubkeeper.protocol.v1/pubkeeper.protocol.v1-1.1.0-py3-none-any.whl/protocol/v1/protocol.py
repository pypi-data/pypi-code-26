"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.protocol.v1.constant import (
    protocol_flags, PUBKEEPER_PROTOCOL_V10, PUBKEEPER_PROTOCOL_V11
)
from pubkeeper.protocol.v1.packet import Packet, PubkeeperPacket, ErrorPacket
from struct import pack, unpack, calcsize, error as struct_error
import ctypes
import json
import logging


class PubkeeperProtocol(object):
    _packet_format_v10 = '<HH4x'
    _packet_format_v11 = '<HHBH1x'

    # Size of the header is not allowed to change in version 1.x
    _packet_format_size = calcsize(_packet_format_v10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger('pubkeeper.protocol.v1')
        self.handlers = {
            Packet.ERROR: self.on_error,
        }

        # Negotiated version, default low
        self.selected_protocol = PUBKEEPER_PROTOCOL_V10

    def unpack(self, data):
        if self.selected_protocol == PUBKEEPER_PROTOCOL_V10:
            packet, payload_len = unpack(
                PubkeeperProtocol._packet_format_v10,
                data[:PubkeeperProtocol._packet_format_size]
            )
        elif self.selected_protocol == PUBKEEPER_PROTOCOL_V11:
            packet, payload_len_low, flags, payload_len_high = unpack(
                PubkeeperProtocol._packet_format_v11,
                data[:PubkeeperProtocol._packet_format_size]
            )

            flag_b = ctypes.c_ubyte(flags)

            if protocol_flags['HIGH_LOW_LENGTH'] & flag_b.value:
                (payload_len, ) = unpack('<I',
                                         pack('<HH', payload_len_low,
                                              payload_len_high))
            else:
                payload_len = payload_len_low

        payload = json.loads(
            unpack('<{}s'.format(payload_len),
                   data[PubkeeperProtocol._packet_format_size:])[0].decode()
        )

        return (packet, payload_len, payload)

    def _write_message(self, message):
        try:
            if isinstance(message, PubkeeperPacket):
                if Packet(message.packet) is Packet.CLIENT_AUTHENTICATE:
                    self.logger.debug("Sending: {0} - *****".
                                      format(Packet(message.packet).name))
                else:
                    self.logger.debug("Sending: {0} - {1}".format(
                        message.packet.name, message.payload))

                self.write_message(message.gen_packet(self.selected_protocol))
            else:
                self.logger.info("Trying to send a non packet")
        except:  # noqa
            self.logger.exception("Could not send")

    def on_message(self, message):
        """Handle Incoming Message

        Will handle incoming messages from WebSocket and send to
        respective handler

        Args
            message (string) - Data received from WebSocket
        """
        try:
            (packet, payload_len, payload) = self.unpack(message)
            if Packet(packet) is Packet.CLIENT_AUTHENTICATE:
                self.logger.debug("Received: {0} - *****".
                                  format(Packet(packet).name))
            else:
                self.logger.debug("Received: {0} - {1}".
                                  format(Packet(packet).name, payload))
            if Packet(packet) in self.handlers:
                self.handlers[Packet(packet)](**payload)
            else:
                self.logger.warning("There is no handler for: {0}".
                                    format(Packet(packet).name))
        except struct_error as e:
            self.logger.error('Invalid packet structure received')
            self._write_message(ErrorPacket(
                message='Action error ({0})'.format(e)
            ))
        except Exception as e:
            if Packet(packet) is not Packet.ERROR:
                self.logger.error('Action error ({0})'.format(e))
                self._write_message(ErrorPacket(
                    message='Action error ({0})'.format(e)
                ))

    def on_error(self, message):
        """on_error

        Called when a ERROR packet is received

        Args:
            message (string) - Error String
        """
        pass
