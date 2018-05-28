import struct
import logging

from .message import Message


def decode(message, topics):
    """
    Convert an MQTTMessage to a Message

    Args:
        message (MQTTMessage):
            A paho.mqtt.MQTTMessage received from any message queue
    """
    data = struct.unpack(topics[0].fmt, message.payload)
    logging.debug(f'Decoded data: {data}')
    return Message(data, topics)
