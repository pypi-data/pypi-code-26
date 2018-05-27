# -*- coding: utf-8 -*-

import sys


# Useful for very coarse version differentiation.
PY3 = sys.version_info[0] == 3

if PY3:
    string_types = (str, )
    import _thread

    from urllib.parse import urlencode, urljoin, urlsplit, urlunsplit, parse_qsl

    def reraise(tp, value, tb=None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        else:
            raise value

else:
    string_types = (str, unicode)
    import thread as _thread

    from urllib import urlencode
    from urlparse import urljoin, urlsplit, urlunsplit, parse_qsl

    exec('''def reraise(tp, value, tb=None):
               raise tp, value, tb
        ''')
