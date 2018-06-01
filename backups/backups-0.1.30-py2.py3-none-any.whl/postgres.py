#!/usr/bin/env python
import sys
from .logging import info, debug


def main():
  info(sys.argv)

  if len(sys.argv) < 2:
    exit('Usage: $0 <data-source> [<database>]')

  try:
    raise NotImplementedError('Adapter postgres is not implemented yet.')

  except Exception as e:
    exit('Error: %s' % (e))


if __name__ == '__main__':
  main()
