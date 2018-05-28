"""
Gabby module witch creates the Gabby class to handle creation of
message queue nodes for intercommunication
"""
import logging
from collections import namedtuple

from .transmitter import Transmitter
from .receiver import Receiver
from .decoder import decode
from .message import Message


Topic = namedtuple('Topic', ['name', 'fmt'])


class Gabby(Transmitter, Receiver):
    def __init__(self, input_topics, output_topics, decode_input=True,
                 url=None, port=None, keepalive=None):
        """
        Processor initializer

        Args:
            topics (collection):
                output topics to send results

            decoder (bool), default=True:
                enable auto encoding/decoding of any received message
        """
        Receiver.__init__(self, input_topics, url, port, keepalive)
        Transmitter.__init__(self, output_topics, url, port, keepalive)
        self.decode_input = decode_input

    def process(self, userdata, message):
        if self.decode_input:
            topic_name = message.topic
            topics = list(
                filter(
                    lambda x: x.name == topic_name,
                    self.input_topics
                )
            )
            message = decode(message, topics)

        logging.debug(f'Processing message: {message}')
        response_messages = self.transform(message)
        for msg in response_messages:
            self.send(msg)

    def transform(self, message):
        """
        Abstract method to process any received message

        Args:
            message (Message or paho.mqtt.MQTTMessage):
                message from queue decoded or not depending on 'decode' var

            author (str):
                message's writer

        Return:
            Collection of messages to be transmitted or an empty list
        """
        return [Message(message.data, self.output_topics)]
