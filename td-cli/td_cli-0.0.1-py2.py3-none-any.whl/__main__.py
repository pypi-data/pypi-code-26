from __future__ import absolute_import

import sys
import os


if __package__ == '':
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, path)


# TODO
import todo


if __name__ == '__main__':
    sys.exit(todo.main())
