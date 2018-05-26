import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pelops import mylogger, mqttclient, read_config
import threading
from time import sleep
from eurydike.eventdetectors.onband import OnBand


class _Tools:
    def _on_response(self, value):
        self.last_message = value.decode("utf-8")
        self.on_response_sync.set()

    def _on_value(self, value):
        self.last_value = value.decode("utf-8")
        self.on_value_sync.set()

    def _publish(self, topic, message):
        self.mqtt_client.publish(topic, message)
        if not self.on_value_sync.wait(1):
            self.fail("Timeout on publishing {}:{}.".format(topic, message))

        if isinstance(message, int):
            self.last_value = int(self.last_value)
        elif isinstance(message, float):
            self.last_value = float(self.last_value)
        else:
            self.fail("Dont know how to handle type '{}'.".format(type(message)))

        if message != self.last_value:
            self.fail("Last value '{}' not identical to last transmitted message '{}' on topic '{}'.".
                      format(self.last_value, message, topic))
        self.on_value_sync.clear()

    def _wait_for_response(self, message):
        if not self.on_response_sync.wait(1):
            self.fail("Timeout waiting on response for message '{}'.".format(message))
        self.on_response_sync.clear()

    def _setUp(self, id):
        conf = read_config.read_config(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))+"/tests_unit/config.yaml")
        self.config = conf["eventdetectors"][id]
        self.mqtt_client = mqttclient.MQTTClient(conf["mqtt"], self.logger, True)

        self.mqtt_client.subscribe(self.topic_pub, self._on_response)
        self.mqtt_client.subscribe(self.topic_sub, self._on_value)
        self.mqtt_client.connect()

        self.on_value_sync = threading.Event()
        self.on_response_sync = threading.Event()
        self.on_value_sync.clear()
        self.on_response_sync.clear()

        self.ed = None
        self.last_message = None
        self.last_value = None


class TestOnBand(unittest.TestCase, _Tools):
    @classmethod
    def setUpClass(cls):
        cls.config = read_config.read_config(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))+"/tests_unit/config.yaml")
        cls.logger = mylogger.create_logger(cls.config["logger"], __name__)
        cls.logger.info("TestOnBand - start")

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestOnBand - stop")

    def setUp(self):
        self.topic_sub = "/test/value"
        self.topic_pub = "/test/band"
        self.on_violation = "event_detected"
        self.on_restoration = "event_ended"
        self._setUp(3)

    def tearDown(self):
        self.mqtt_client.disconnect()

    def test_inside_init(self):
        self.ed = OnBand(self.config, self.logger, self.mqtt_client)
        self.assertEqual(self.ed._lower_threshold, 7.0)
        self.assertEqual(self.ed._upper_threshold, 8.0)
        self.assertEqual(self.ed._topic_sub, self.topic_sub)
        self.assertEqual(self.ed._topic_pub, self.topic_pub)
        self.assertEqual(self.ed._responses["on-violation"], self.on_violation)
        self.assertEqual(self.ed._responses["on-restoration"], self.on_restoration)
        self.assertFalse(self.ed._event_active)

    def test_inside_lower_lt_upper(self):
        config = self.config
        config["lower-threshold"] = 8
        config["upper-threshold"] = 7
        self.assertRaises(ValueError, OnBand, config, self.logger, self.mqtt_client)

    def test_inside_start(self):
        self.ed = OnBand(self.config, self.logger, self.mqtt_client)
        self.ed.start()
        try:
            temp = self.mqtt_client._topic_handler[self.topic_sub]
            self.assertIn(self.ed._message_handler, temp)
        except KeyError:
            self.fail("No handler registered in mqtt client for topic '{}'.".format(self.topic_sub))

    def test_inside_steps(self):
        self.ed = OnBand(self.config, self.logger, self.mqtt_client)
        self.ed.start()

        self._publish(self.topic_sub, 7.1)
        sleep(0.1)
        self.assertFalse(self.ed._event_active)
        self.assertIsNone(self.last_message)

        self._publish(self.topic_sub, 7.0)
        sleep(0.1)
        self.assertFalse(self.ed._event_active)
        self.assertIsNone(self.last_message)

        self._publish(self.topic_sub, 6.9)
        self._wait_for_response(7.0)
        self.assertTrue(self.ed._event_active)
        self.assertIsNotNone(self.last_message)
        self.assertEqual(self.last_message, self.on_violation)
        self.last_message = None

        self._publish(self.topic_sub, 6.8)
        sleep(0.1)
        self.assertTrue(self.ed._event_active)
        self.assertIsNone(self.last_message)

        self._publish(self.topic_sub, 8.2)
        sleep(0.1)
        self.assertTrue(self.ed._event_active)
        self.assertIsNone(self.last_message)

        self._publish(self.topic_sub, 8.1)
        sleep(0.1)
        self.assertTrue(self.ed._event_active)
        self.assertIsNone(self.last_message)

        self._publish(self.topic_sub, 8.0)
        self._wait_for_response(8.0)
        self.assertFalse(self.ed._event_active)
        self.assertIsNotNone(self.last_message)
        self.assertEqual(self.last_message, self.on_restoration)
        self.last_message = None

        self._publish(self.topic_sub, 7.9)
        sleep(0.1)
        self.assertFalse(self.ed._event_active)
        self.assertIsNone(self.last_message)

    def test_inside_stop(self):
        self.ed = OnBand(self.config, self.logger, self.mqtt_client)
        self.ed.start()
        self.ed.stop()
        try:
            temp = self.mqtt_client._topic_handler[self.topic_sub]
            self.assertNotIn(self.ed._message_handler, temp)
        except KeyError:
            pass


if __name__ == '__main__':
    unittest.main()
