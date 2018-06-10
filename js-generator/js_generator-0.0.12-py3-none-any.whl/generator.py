#!/usr/bin/env python
import argparse
from constants import MESSAGES, TYPES
from utils import Utils
from validations import Validations

utils = Utils()
validations = Validations()


class Main:
    parser = None

    def __init__(self):
        self.parser = argparse.ArgumentParser(description=MESSAGES.get('title'))
        self.set_args()
        self.process_args()

    def set_args(self):
        self.parser.add_argument('--full-state', help=MESSAGES.get('full_state'))
        self.parser.add_argument('--filename', help=MESSAGES.get('filename'))
        self.parser.add_argument('--type', help='one of {}'.format(TYPES))
        self.parser.add_argument('--classname', help=MESSAGES.get('class_name'))

    def process_args(self):
        args = self.parser.parse_args()
        valid = validations.validate(args)

        if valid:
            utils.create(args)

Main()
