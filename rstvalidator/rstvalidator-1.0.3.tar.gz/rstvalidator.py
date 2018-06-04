#!/usr/bin/env python
import os
import sys
from docutils import utils
from docutils.core import publish_parts
from public import public

# 'pygments' required

reports = []

orignal_system_message = utils.Reporter.system_message


def rst2html(value):
    """ Run rst2html translation """
    parts = publish_parts(source=value, writer_name="html4css1")
    return parts['whole']


def system_message(self, level, message, *children, **kwargs):
    args = [self, level, message] + list(children)
    result = orignal_system_message(*args, **kwargs)
    if level >= self.WARNING_LEVEL:
        # All reST failures preventing doc publishing go to reports
        # and thus will result to failed checkdocs run
        sys.modules[__name__].reports.append(message)
    return result


@public
def rstvalidator(path):

    sys.modules[__name__].reports = []

    text = open(path).read()
    # Monkeypatch docutils for simple error/warning output support
    utils.Reporter.system_message = system_message
    old_stderr = sys.stderr
    sys.stderr = open(os.devnull, "w")
    try:
        rst2html(text)
        utils.Reporter.system_message = orignal_system_message
        return reports
    finally:
        sys.stderr.close()
        sys.stderr = old_stderr


USAGE = "usage: python -m rstvalidator path ..."

if __name__ == "__main__":
    argv = sys.argv
    if len(argv) == 1 or (len(argv) == 2 and argv[1] == "--help"):
        print(USAGE)
    else:
        for path in argv[1:]:
            reports = rstvalidator(path)
            if reports:
                print(path)
                print("\n".join(map(str, reports)))
                sys.exit(1)
