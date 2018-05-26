import unittest
import threading
from time import sleep
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pelops import mylogger, mqttclient, read_config
from eurydike.eventdetectors.onthreshold import OnThreshold, Comparator


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
        self.logger = mylogger.create_logger(conf["logger"], __name__)
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


class TestOnThresholdBelow(unittest.TestCase, _Tools):
    def setUp(self):
        self.topic_sub = "/test/value"
        self.topic_pub = "/test/below"
        self.on_violation = "event_detected"
        self.on_restoration = "event_ended"
        self._setUp(1)

    def tearDown(self):
        self.mqtt_client.disconnect()

    def test_below_init(self):
        self.ed = OnThreshold(self.config, self.logger, self.mqtt_client)
        self.assertEqual(self.ed._comparator, Comparator.LOWERTHAN)
        self.assertEqual(self.ed._threshold, 7.0)
        self.assertEqual(self.ed._topic_sub, self.topic_sub)
        self.assertEqual(self.ed._topic_pub, self.topic_pub)
        self.assertEqual(self.ed._responses["on-violation"], self.on_violation)
        self.assertEqual(self.ed._responses["on-restoration"], self.on_restoration)
        self.assertFalse(self.ed._event_active)

    def test_below_start(self):
        self.ed = OnThreshold(self.config, self.logger, self.mqtt_client)
        self.ed.start()
        try:
            temp = self.mqtt_client._topic_handler[self.topic_sub]
            self.assertIn(self.ed._message_handler, temp)
        except KeyError:
            self.fail("No handler registered in mqtt client for topic '{}'.".format(self.topic_sub))

    def test_below_steps(self):
        self.ed = OnThreshold(self.config, self.logger, self.mqtt_client)
        self.ed.start()

        self._publish(self.topic_sub, 7.2)
        sleep(0.1)
        self.assertFalse(self.ed._event_active)
        self.assertIsNone(self.last_message)

        self._publish(self.topic_sub, 7.1)
        sleep(0.1)
        self.assertFalse(self.ed._event_active)
        self.assertIsNone(self.last_message)

        self._publish(self.topic_sub, 7)
        sleep(0.1)
        self.assertFalse(self.ed._event_active)
        self.assertIsNone(self.last_message)

        self._publish(self.topic_sub, 6.9)
        self._wait_for_response(6.9)
        self.assertTrue(self.ed._event_active)
        self.assertIsNotNone(self.last_message)
        self.assertEqual(self.last_message, self.on_violation)
        self.last_message = None

        self._publish(self.topic_sub, 6.8)
        sleep(0.1)
        self.assertTrue(self.ed._event_active)
        self.assertIsNone(self.last_message)

        self._publish(self.topic_sub, 7)
        self._wait_for_response(7)
        self.assertFalse(self.ed._event_active)
        self.assertIsNotNone(self.last_message)
        self.assertEqual(self.last_message, self.on_restoration)
        self.last_message = None

        self._publish(self.topic_sub, 7)
        sleep(0.1)
        self.assertFalse(self.ed._event_active)
        self.assertIsNone(self.last_message)

    def test_below_stop(self):
        self.ed = OnThreshold(self.config, self.logger, self.mqtt_client)
        self.ed.start()
        self.ed.stop()
        try:
            temp = self.mqtt_client._topic_handler[self.topic_sub]
            self.assertNotIn(self.ed._message_handler, temp)
        except KeyError:
            pass


class TestOnThresholdAbove(unittest.TestCase, _Tools):
    def setUp(self):
        self.topic_sub = "/test/value"
        self.topic_pub = "/test/above"
        self.on_violation = "event_detected"
        self.on_restoration = "event_ended"
        self._setUp(0)

    def tearDown(self):
        self.mqtt_client.disconnect()

    def test_above_init(self):
        self.ed = OnThreshold(self.config, self.logger, self.mqtt_client)
        self.assertEqual(self.ed._comparator, Comparator.GREATERTHAN)
        self.assertEqual(self.ed._threshold, 7.0)
        self.assertEqual(self.ed._topic_sub, self.topic_sub)
        self.assertEqual(self.ed._topic_pub, self.topic_pub)
        self.assertNotIn("on-violation", self.ed._responses)
        self.assertEqual(self.ed._responses["on-restoration"], self.on_restoration)
        self.assertFalse(self.ed._event_active)

    def test_above_start(self):
        self.ed = OnThreshold(self.config, self.logger, self.mqtt_client)
        self.ed.start()
        try:
            temp = self.mqtt_client._topic_handler[self.topic_sub]
            self.assertIn(self.ed._message_handler, temp)
        except KeyError:
            self.fail("No handler registered in mqtt client for topic '{}'.".format(self.topic_sub))

    def test_above_steps(self):
        self.ed = OnThreshold(self.config, self.logger, self.mqtt_client)
        self.ed.start()

        self._publish(self.topic_sub, 6.8)
        sleep(0.1)
        self.assertFalse(self.ed._event_active)
        self.assertIsNone(self.last_message)

        self._publish(self.topic_sub, 6.9)
        sleep(0.1)
        self.assertFalse(self.ed._event_active)
        self.assertIsNone(self.last_message)

        self._publish(self.topic_sub, 7)
        sleep(0.1)
        self.assertFalse(self.ed._event_active)
        self.assertIsNone(self.last_message)

        self._publish(self.topic_sub, 7.1)
        sleep(0.1)
        self.assertTrue(self.ed._event_active)
        self.assertIsNone(self.last_message)

        self._publish(self.topic_sub, 7.2)
        sleep(0.1)
        self.assertTrue(self.ed._event_active)
        self.assertIsNone(self.last_message)

        self._publish(self.topic_sub, 7)
        self._wait_for_response(7)
        self.assertFalse(self.ed._event_active)
        self.assertIsNotNone(self.last_message)
        self.assertEqual(self.last_message, self.on_restoration)
        self.last_message = None

        self._publish(self.topic_sub, 7)
        sleep(0.1)
        self.assertFalse(self.ed._event_active)
        self.assertIsNone(self.last_message)

    def test_above_stop(self):
        self.ed = OnThreshold(self.config, self.logger, self.mqtt_client)
        self.ed.start()
        self.ed.stop()
        try:
            temp = self.mqtt_client._topic_handler[self.topic_sub]
            self.assertNotIn(self.ed._message_handler, temp)
        except KeyError:
            pass


class TestOnThresholdEqual(unittest.TestCase, _Tools):
    def setUp(self):
        self.topic_sub = "/test/value"
        self.topic_pub = "/test/equal"
        self.on_violation = "event_detected"
        self.on_restoration = "event_ended"
        self._setUp(2)

    def tearDown(self):
        self.mqtt_client.disconnect()

    def test_equal_init(self):
        self.ed = OnThreshold(self.config, self.logger, self.mqtt_client)
        self.assertEqual(self.ed._comparator, Comparator.EQUALTO)
        self.assertEqual(self.ed._threshold, 7.0)
        self.assertEqual(self.ed._topic_sub, self.topic_sub)
        self.assertEqual(self.ed._topic_pub, self.topic_pub)
        self.assertEqual(self.ed._responses["on-violation"], self.on_violation)
        self.assertNotIn("on-restoration", self.ed._responses)
        self.assertFalse(self.ed._event_active)

    def test_equal_start(self):
        self.ed = OnThreshold(self.config, self.logger, self.mqtt_client)
        self.ed.start()
        try:
            temp = self.mqtt_client._topic_handler[self.topic_sub]
            self.assertIn(self.ed._message_handler, temp)
        except KeyError:
            self.fail("No handler registered in mqtt client for topic '{}'.".format(self.topic_sub))

    def test_equal_steps(self):
        self.ed = OnThreshold(self.config, self.logger, self.mqtt_client)
        self.ed.start()

        self._publish(self.topic_sub, 6.9)
        sleep(0.1)
        self.assertFalse(self.ed._event_active)
        self.assertIsNone(self.last_message)

        self._publish(self.topic_sub, 7.0)
        self._wait_for_response(7.0)
        self.assertTrue(self.ed._event_active)
        self.assertIsNotNone(self.last_message)
        self.assertEqual(self.last_message, self.on_violation)
        self.last_message = None

        self._publish(self.topic_sub, 7.0)
        sleep(0.1)
        self.assertTrue(self.ed._event_active)
        self.assertIsNone(self.last_message)

        self._publish(self.topic_sub, 7.1)
        sleep(0.1)
        self.assertFalse(self.ed._event_active)
        self.assertIsNone(self.last_message)

    def test_equal_stop(self):
        self.ed = OnThreshold(self.config, self.logger, self.mqtt_client)
        self.ed.start()
        self.ed.stop()
        try:
            temp = self.mqtt_client._topic_handler[self.topic_sub]
            self.assertNotIn(self.ed._message_handler, temp)
        except KeyError:
            pass


if __name__ == '__main__':
    unittest.main()
