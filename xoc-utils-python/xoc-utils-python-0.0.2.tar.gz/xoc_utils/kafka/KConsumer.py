# -*- coding: utf-8 -*-
#pylint: disable-msg=too-many-arguments
#pylint: disable-msg=too-many-instance-attributes

import time
import json
import traceback
from confluent_kafka import Consumer, KafkaError, KafkaException
from xoc_utils import Singleton
from xoc_utils.kafka import KProducer

class KConsumer(metaclass=Singleton):
    def __init__(self,
                 server_origin,
                 group_id,
                 service_name,
                 poll_timeout=3.0,
                 auto_commit_enable=False,
                 auto_commit_interval=0,
                 dead_letter_topic='xoc.dead-letter-queue',
                 retries=3):

        self.server_origin = server_origin
        self.group_id = group_id
        self.poll_timeout = poll_timeout
        self.service_name = service_name
        self.dead_letter_topic = dead_letter_topic
        self.retries = retries
        self.k_consumer = Consumer({
            'bootstrap.servers': server_origin,
            'group.id': group_id,
            'default.topic.config': {'auto.offset.reset': 'latest'},
            'auto.commit.enable': auto_commit_enable,
            'auto.commit.interval.ms': auto_commit_interval
        })
        self.stopped = False
        self.handlers = {}
        self.k_producer = KProducer(server_origin, service_name)


    def add_handler(self, topic, handler):
        self.handlers[topic] = handler

    @staticmethod
    def _log_assignment(consumer, partitions):
        """
            Helper function to log assignment once consumer subscribe to Kafka service successfully.
        """
        print('Assignment:' + ', '.join(str(e) for e in partitions))

    @staticmethod
    def _create_error(ex):
        return {
            'exception': str(ex),
            '@timestamp': time.time()
        }

    def _handle_exception(self, ex, msg, targetTopic):
        new_msg_obj = None
        msg_obj = None

        try:
            msg_obj = json.loads(msg.value())
        except Exception:
            self.k_producer.produce(self.dead_letter_topic, msg.value())
            return

        # If retries is 0, push to dead letter topic
        if self.retries == 0:
            self.k_producer.produce(self.dead_letter_topic, msg.value())
            return

        if msg.topic().endswith('-retry'):
            new_msg_obj = msg_obj
            errors = new_msg_obj['retry']['errors']

            if len(errors) > self.retries:
                targetTopic = self.dead_letter_topic
            else:
                errors.append(self._create_error(ex))
                new_msg_obj['retry']['errors'] = errors
        else:
            error = self._create_error(ex)
            new_msg_obj = {
                'message': msg_obj,
                'retry': {
                    'service': self.service_name,
                    'topic': msg.topic(),
                    'errors': [error]
                }
            }
        self.k_producer.produce(targetTopic, json.dumps(new_msg_obj))

    def _consume_message(self, msg):

        targetTopic = msg.topic() + '-retry'
        try:
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    return
                else:
                    targetTopic = self.dead_letter_topic
                    raise KafkaException(msg.error())
            else:
                print('Received message: {}, partition: {}, offset: {}'.format(
                    msg.value().decode('utf-8'),
                    msg.partition(),
                    msg.offset()))

                originTopic = msg.topic()
                message = msg.value()

                if msg.topic().endswith('-retry'):
                    targetTopic = msg.topic()
                    msg_obj = json.loads(msg.value())
                    originTopic = msg_obj['retry']['topic']
                    message = json.dumps(msg_obj['message'])

                self.handlers[originTopic](message)
        except Exception as ex:
            traceback.print_exc()
            self._handle_exception(ex, msg, targetTopic)

    def stop(self):
        self.stopped = True

    def consume(self):
        """
            Start to consume, this method should be in a separate thread/process,
            because it requires a while loop to sync with Kafka service.

            Kafka consumer will subscribe all the registered topic handler pairs
            to Kafka service, then start to sync with service by polling.
        """
        self.k_consumer.subscribe(
            list(self.handlers.keys()), on_assign=self._log_assignment)

        try:
            while True:
                if self.stopped:
                    break
                msg = self.k_consumer.poll(self.poll_timeout)
                if msg is None:
                    continue
                self._consume_message(msg)
                self.k_consumer.commit(msg)
        except KeyboardInterrupt:
            print('%% Aborted by user\n')

        self.k_consumer.close()
