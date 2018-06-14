#!/usr/bin/env python3

import logging
import unittest
import os
import random
import sys
import json

from faker import Faker
from faker.providers import BaseProvider

from python3_json_log_formatter import JsonFormatter

THIS_FILE = os.path.abspath(__file__)

fake = Faker()


def line_count(path):
    with open(path) as f:
        return len([x for x in f])
    return None


class FakeLoggingProvider(BaseProvider):

    def log_level(self):
        """ Return a random log level. """
        return getattr(logging,
                       random.choice(list(logging._levelToName.values()))
                       )

    def log_record(self, msg, args):
        """ Return a fake log instance. """
        return logging.LogRecord(
            name=fake.word(),
            level=self.log_level(),
            pathname=THIS_FILE,
            lineno=random.randint(1, line_count(THIS_FILE)),
            msg=msg,
            args=args,
            exc_info=sys.exc_info()
        )


fake.add_provider(FakeLoggingProvider)


class TestFormatter(unittest.TestCase):

    def test_complex_formatting(self):
        jf = JsonFormatter()
        msg = "Float: %f, String: %s, Integer: %d, Character: %c"
        args = ("1.2", "string here", "6", 's')
        args2 = (1.2, "string here", 6, 's')
        expected = msg % args2
        result = jf.format(fake.log_record(msg, args))
        self.assertEqual(expected, json.loads(result)['msg'])
