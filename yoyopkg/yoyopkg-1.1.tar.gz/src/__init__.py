import sys

import os

from src.yoyo import run


def main():

    try:
        run(os.path.realpath(__file__))
    except KeyboardInterrupt:
        sys.exit(0)
