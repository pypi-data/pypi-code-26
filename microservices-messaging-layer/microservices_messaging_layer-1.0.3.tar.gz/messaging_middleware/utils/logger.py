import logging
import sys
import json
import os
from messaging_middleware.avro_communication_layer.Producer import Producer

monitoring_config_file = os.environ.get('monitoring_config_file','configuration/monitor.json')
monitoring_config = json.load(open(monitoring_config_file)).get('monitoring', None)

bootstrap_servers = monitoring_config['bootstrap_servers']
monitor_topic = monitoring_config['monitor_topic']
schema_reqistry_url = monitoring_config['schema_reqistry_url']


def delivery_callback(err, msg):
    if err:
        sys.stderr.write('%% Logger - Message failed delivery: %s\n' % err)
    else:
        sys.stderr.write('%% Logger - Message delivered to %s [%d] @ %o\n' %
                         (msg.topic(), msg.partition(), msg.offset()))


class Logger:
    __instance = None

    def __new__(cls):
        if Logger.__instance is None:
            logger = logging.getLogger()
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
            logger.debug('Logger ready, my Lord.')
            Logger.__instance = object.__new__(cls)
            Logger.__instance.logger = logger
            "'Kafka producer'"
            logging.basicConfig(
                format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
                level=logging.INFO
            )
            logging.getLogger('urllib3').setLevel(logging.ERROR)
            logger.producer = Producer(bootstrap_servers=bootstrap_servers,
                                       schema_reqistry_url=schema_reqistry_url, topic=monitor_topic)

        return Logger.__instance



    def logmsg(self, level=None, *args):
        # self.logger.setLevel(logging.WARNING)
        """
        logger.debug('debug message')
        logger.info('info message')
        logger.warn('warn message')
        logger.error('error message')
        logger.critical('critical message')
        """
        if level == 'debug':
            return self.logger.debug(args)
        if level == 'info':
            return self.logger.info(args)
        if level == 'warn':
            return self.logger.warn(args)
        if level == 'error':
            return self.logger.error(args)
        if level == 'critical':
            return self.logger.critical(args)
        else:
            return self.logger.debug(args)

    def produce_msg(self, message):
        return self.logger.producer.produce_message(value=message['value'], key=message['key'],
                                                    callback=delivery_callback)


    def retry(self,**kwargs):
        pass
