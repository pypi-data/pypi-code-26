#!/usr/bin/env python3

from copy import deepcopy
import sys
import argparse
import re

# https://github.com/semver/semver.org/issues/59
_SEMVER_REGEX = '^(?P<VersionTripple>(?P<Major>0|[1-9][0-9]*)\.(?P<Minor>0|[1-9][0-9]*)\.(?P<Patch>0|[1-9][0-9]*)){1}(?P<Tags>(?:\-(?P<Prerelease>(?:(?=[0]{1}[0-9A-Za-z-]{0})(?:[0]{1})|(?=[1-9]{1}[0-9]*[A-Za-z]{0})(?:[0-9]+)|(?=[0-9]*[A-Za-z-]+[0-9A-Za-z-]*)(?:[0-9A-Za-z-]+)){1}(?:\.(?=[0]{1}[0-9A-Za-z-]{0})(?:[0]{1})|\.(?=[1-9]{1}[0-9]*[A-Za-z]{0})(?:[0-9]+)|\.(?=[0-9]*[A-Za-z-]+[0-9A-Za-z-]*)(?:[0-9A-Za-z-]+))*){1}){0,1}(?:\+(?P<Meta>(?:[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))){0,1})$'

_SEMVER_PATTERN = re.compile(_SEMVER_REGEX)

#
# Parse commandline arguments
#
def _parse_arguments(args):
  parser = argparse.ArgumentParser(description='Semantic versioning tool')
  parser.add_argument('version', nargs='?', help='Semantic version')
  parser.add_argument('--type', choices=['major', 'minor', 'patch'], default='patch', help='Semantic version part to process, defaults to PATCH')
  parser.add_argument('-s', '--step', type=int, default=1, help='Increment/decrement for --inc/--dec')

  inc_dec_group = parser.add_mutually_exclusive_group()
  inc_dec_group.add_argument('-i', '--inc', action='store_true', help='Increase version defined with --type [type]')
  inc_dec_group.add_argument('-d', '--dec', action='store_true', help='Decrease version defined with --type [type]')


  if not len(sys.argv) > 1:
    parser.print_help()
    sys.exit(0)
  
  return parser.parse_args(args)

#
# Validate version string
#
def _validate_version(version):
  if not is_valid(version):
    raise Exception('{} is not a valid semantic version'.format(version))

#
# Validate input against semantic
# versioning rules
#
def is_valid(input) : return bool(_SEMVER_PATTERN.match(input))

#
# Parse semantic version string
#
def parse(version):
  match = _SEMVER_PATTERN.match(version)

  if not match:
    raise Exception('{} did not match semantic versioning rules'.format(version))

  return {
    'major': int(match.group('Major')),
    'minor': int(match.group('Minor')),
    'patch': int(match.group('Patch')),
    'tags': list(filter(None, match.group('Tags').split('-'))),
    'prerelease': match.group('Prerelease')
  }

#
# Increase given type of the version
#
def increase(version, type, increment=1):
  copy = deepcopy(version)
  copy[type] += increment
  return copy

#
# Decrease given type of version
#
def decrease(version, type, decrement=1):
  copy = deepcopy(version)
  copy[type] -= decrement

  if copy[type] < 0:
    raise Exception('Cannot decrease {} version below zero'.format(type))

  return copy

#
# Serialize version to string
#
def serialize(version):
  return '{}.{}.{}{}'.format(
    version['major'],
    version['minor'],
    version['patch'],
    '-' + version['prerelease'] if version['prerelease'] else ''
  )
