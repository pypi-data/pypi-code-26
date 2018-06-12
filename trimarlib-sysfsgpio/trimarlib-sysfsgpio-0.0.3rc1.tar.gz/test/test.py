import unittest
import sysfsgpio
import functools

class TestSysfsgpioPin(unittest.TestCase):
    PINS = None

    @classmethod
    def setUpClass(cls):
        cls.PINS = sysfsgpio.get_pins()

    def test_type(self):
        for i in range(len(self.PINS)):
            with self.subTest(i=i):
                self.assertIs(type(self.PINS[i]), sysfsgpio.Pin)

    def test_pin(self):
        for i in range(len(self.PINS)):
            with self.subTest(i=i):
                self.assertIs(type(self.PINS[i].pin), int)
                with self.assertRaises(AttributeError):
                    self.PINS[i].pin = 13

    def test_pinname(self):
        for i in range(len(self.PINS)):
            with self.subTest(i=i):
                self.assertIs(type(self.PINS[i].pinname), str)
                with self.assertRaises(AttributeError):
                    self.PINS[i].pinname = 'abc'

    def test_event(self):
        for i in range(len(self.PINS)):
            with self.subTest(i=i):
                self.assertIs(type(self.PINS[i].input_changed), sysfsgpio.Event)
                with self.assertRaises(TypeError):
                    self.PINS[i].input_changed = 'asd'

    def test_value(self):
        for i in range(len(self.PINS)):
            with self.subTest(i=i):
                self.assertIs(type(self.PINS[i].value), int)
                with self.assertRaises(PermissionError):
                    self.PINS[i].value = 0
                self.PINS[i].direction = 'out'
                for vv in [('1', 1), ('0', 0), (True, 1), (False, 0), (3.14, True)]:
                    self.PINS[i].value = vv[0]
                    self.assertEqual(self.PINS[i].value, vv[1])
                with self.assertRaises(ValueError):
                    self.PINS[i].value = 'asd'
                self.PINS[i].value = 0
                self.PINS[i].direction = 'in'

    def test_invert(self):
        for i in range(len(self.PINS)):
            with self.subTest(i=i):
                self.assertIs(type(self.PINS[i].invert), bool)
                for vv in [('1', True), ('0', False), (1, True), (0, False), (3.14, True)]:
                    self.PINS[i].invert = vv[0]
                    self.assertEqual(self.PINS[i].invert, vv[1])
                with self.assertRaises(ValueError):
                    self.PINS[i].invert = 'asd'
                self.PINS[i].invert = 0

    def test_direction(self):
        for i in range(len(self.PINS)):
            with self.subTest(i=i):
                self.assertIs(type(self.PINS[i].direction), str)
                with self.assertRaises(TypeError):
                    self.PINS[i].direction = 3
                with self.assertRaises(ValueError):
                    self.PINS[i].direction = 'asd'
                for vv in ['out', 'in']:
                    self.PINS[i].direction = vv
                    self.assertEqual(self.PINS[i].direction, vv)

    def test_config(self):
        for i in range(len(self.PINS)):
            with self.subTest(i=i):
                cfg = self.PINS[i].config()
                self.assertIs(type(cfg), dict)
                for key in ['debounce', 'ontime', 'offtime']:
                    self.assertIn(key, cfg)
                    self.assertIs(type(cfg[key]), float)
                self.assertIn('repeat', cfg)
                self.assertIs(type(cfg['repeat']), int)
                for key in ['debounce', 'ontime', 'offtime', 'repeat']:
                    with self.assertRaises(TypeError):
                        self.PINS[i].config({key: 'asd'})

    def test_enabled(self):
        for i in range(len(self.PINS)):
            with self.subTest(i=i):
                self.assertIs(type(self.PINS[i].enabled), bool)
