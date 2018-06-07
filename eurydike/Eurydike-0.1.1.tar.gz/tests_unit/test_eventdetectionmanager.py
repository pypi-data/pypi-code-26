import unittest
import os
import threading
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pelops import mylogger, mqttclient, read_config
from eurydike.eventdetectionmanager import EventDetectionManager
from time import sleep


class _Tools:
    def _on_response_below(self, value):
        self.last_response_below = value.decode("utf-8")
        self.on_response_below_sync.set()

    def _on_response_outside(self, value):
        self.last_response_outside = value.decode("utf-8")
        self.on_response_outside_sync.set()

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

    def _wait_for_response_outside(self, message):
        if not self.on_response_outside_sync.wait(1):
            self.fail("Timeout waiting on outside response for message '{}'.".format(message))
        self.on_response_outside_sync.clear()

    def _wait_for_response_below(self, message):
        if not self.on_response_below_sync.wait(1):
            self.fail("Timeout waiting on below response for message '{}'.".format(message))
        self.on_response_below_sync.clear()

    def _setUp(self):
        self.mqtt_client = mqttclient.MQTTClient(self.config["mqtt"], self.logger, True)

        self.mqtt_client.subscribe(self.topic_pub_below, self._on_response_below)
        self.mqtt_client.subscribe(self.topic_pub_outside, self._on_response_outside)
        self.mqtt_client.subscribe(self.topic_sub, self._on_value)
        self.mqtt_client.connect()

        self.on_value_sync = threading.Event()
        self.on_value_sync.clear()
        self.on_response_below_sync = threading.Event()
        self.on_response_below_sync.clear()
        self.on_response_outside_sync = threading.Event()
        self.on_response_outside_sync.clear()

        sleep(0.1)
        edm = None
        self.last_response_below = None
        self.last_response_outside = None
        self.last_value = None


class TestEventDetectionManager(unittest.TestCase, _Tools):
    @classmethod
    def setUpClass(cls):
        cls.config = read_config.read_config(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))+"/tests_unit/config.yaml")
        cls.logger = mylogger.create_logger(cls.config["logger"], __name__)
        cls.logger.info("TestEventDetectionManager - start")

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestEventDetectionManager - stop")

    def setUp(self):
        self.topic_sub = "/test/value"
        self.topic_pub_below = "/test/below"
        self.topic_pub_outside = "/test/band"
        self.on_violation = "event_detected"
        self.on_restoration = "event_ended"
        self._setUp()

    def tearDown(self):
        self.mqtt_client.disconnect()
        self.mqtt_client = None

    def test_edm_init(self):
        edm = EventDetectionManager(self.config, self.mqtt_client, self.logger)
        self.assertEqual(len(edm._event_detectors), 2)
        self.assertEqual(edm._event_detectors[0]._name, "below")
        self.assertEqual(edm._event_detectors[1]._name, "outside")

    def test_edm_start(self):
        edm = EventDetectionManager(self.config, self.mqtt_client, self.logger)
        edm.start()
        try:
            self.assertIn(edm._event_detectors[0]._message_handler,
                          edm._mqtt_client._topic_handler[self.topic_sub])
            self.assertIn(edm._event_detectors[1]._message_handler,
                          edm._mqtt_client._topic_handler[self.topic_sub])
        except KeyError:
            self.fail("No handler registered in mqtt client for topic '{}'.".format(self.topic_sub))

    def test_edm_steps(self):
        edm = EventDetectionManager(self.config, self.mqtt_client, self.logger)
        edm.start()
        ed_below = edm._event_detectors[0]
        ed_outside = edm._event_detectors[1]

        self._publish(self.topic_sub, 7.1)
        sleep(0.1)
        self.assertFalse(ed_below._event_active)
        self.assertIsNone(self.last_response_below)
        self.assertFalse(ed_outside._event_active)
        self.assertIsNone(self.last_response_outside)

        self._publish(self.topic_sub, 7.0)
        sleep(0.1)
        self.assertFalse(ed_below._event_active)
        self.assertIsNone(self.last_response_below)
        self.assertFalse(ed_outside._event_active)
        self.assertIsNone(self.last_response_outside)

        self._publish(self.topic_sub, 6.9)
        sleep(0.1)
        self._wait_for_response_outside(6.9)
        self._wait_for_response_below(6.9)
        self.assertTrue(ed_below._event_active)
        self.assertIsNotNone(self.last_response_below)
        self.assertTrue(ed_outside._event_active)
        self.assertIsNotNone(self.last_response_outside)
        self.assertEqual(self.last_response_below, self.on_violation)
        self.assertEqual(self.last_response_outside, self.on_violation)
        self.last_response_below = None
        self.last_response_outside = None

        self._publish(self.topic_sub, 8.1)
        self._wait_for_response_below(8.1)
        sleep(0.1)
        self.assertFalse(ed_below._event_active)
        self.assertIsNotNone(self.last_response_below)
        self.assertEqual(self.last_response_below, self.on_restoration)
        self.last_response_below = None
        self.assertTrue(ed_outside._event_active)
        self.assertIsNone(self.last_response_outside)

        self._publish(self.topic_sub, 7.2)
        self._wait_for_response_outside(7.2)
        sleep(0.1)
        self.assertFalse(ed_below._event_active)
        self.assertIsNone(self.last_response_below)
        self.assertFalse(ed_outside._event_active)
        self.assertIsNotNone(self.last_response_outside)
        self.assertEqual(self.last_response_outside, self.on_restoration)
        self.last_response_outside = None

    def test_edm_stop(self):
        edm = EventDetectionManager(self.config, self.mqtt_client, self.logger)
        edm.start()
        edm.stop()
        try:
            self.assertNotIn(edm._event_detectors[0]._message_handler,
                             edm._mqtt_client._topic_handler[self.topic_sub])
            self.assertNotIn(edm._event_detectors[1]._message_handler,
                             edm._mqtt_client._topic_handler[self.topic_sub])
        except KeyError:
            pass


if __name__ == '__main__':
    unittest.main()

