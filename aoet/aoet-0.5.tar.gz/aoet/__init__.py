import argparse
import logging
import sys

__version__ = '0.5'


REQUESTS_FILE = 'requests.json'
TST_FILE = 'tst.json'
PRD_FILE = 'prd.json'

MATRIX_IMAGE = 'points.png'

BODY_MATRIX  = 'body.csv'
UNIQUES_LIST = 'uniques.json'

DATA_FILE = 'results.json'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('aoet')

args = sys.argv[1:]
if '--debug' in args:
    args.remove('--debug')
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

if '--no-logo' in args:
    args.remove('--no-logo')
else:
    logger.info('-' * 13 + 'Automation of Exploratory Testing ' + '-' * 13)
    logger.info(' ' * 30 + 'v ' + __version__)
    logger.info('-' * 60)


import aoet.parser.matrix_parser as matrix_parser
import aoet.analysis.analyzer as analyzer
import aoet.proxy.splitter as splitter

parser = argparse.ArgumentParser(prog='aoet', description='Automation of Exploratory Testing')
parser.add_argument('--version', action='version', version=__version__)
subparsers = parser.add_subparsers()

splitter.add_subparsers(subparsers)
matrix_parser.add_subparsers(subparsers)
analyzer.add_subparsers(subparsers)

def main():
    parsed = parser.parse_args(args=args)
    if hasattr(parsed, 'func'):
        func = parsed.func
        func(parsed)
