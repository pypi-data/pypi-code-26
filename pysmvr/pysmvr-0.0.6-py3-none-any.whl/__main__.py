#!/usr/bin/env python3

import pysmvr.core as core
import sys
import logging

logger = logging.getLogger(__name__)

#
# Entrypoint
#
def main():
  try:
    args = core._parse_arguments(sys.argv[1:])

    if 'version' in args:
      input = args.version
      core._validate_version(input)

      version = core.parse(input)

      if args.inc:
        new_version = core.increase(version, args.type, args.step)
        print(core.serialize(new_version))

      elif args.dec:
        new_version = core.decrease(version, args.type, args.step)
        print(core.serialize(new_version))

  except Exception as e:
    logger.error(e)
    sys.exit(1)

if __name__ == "__main__":
  main()
