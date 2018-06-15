# -*- coding: utf-8 -*-
"""The 'NetFiles' module provides basic extensions for 'os.path.normpath'.  

.. warning::

   This module is currently an experimental release for discussion 
   and may change. Do not use it in production code!

The following subset of URLs / RFC...
"""
from __future__ import absolute_import

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez" \
                " @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.1.20'
__uuid__ = "4135ab0f-fbb8-45a2-a6b1-80d96c164b72"

__docformat__ = "restructuredtext en"

import os
import sys
version = '{0}.{1}'.format(*sys.version_info[:2])
if version < '2.7':  # pragma: no cover
    raise Exception("Requires Python-2.7.* or higher")


class NetFilesException(Exception):
    pass


#
# for test and development
_mydebug = False

#
# supported URIs
#
import re
# keyword patterns and match vector indexes
_COMP = re.compile(
    r"(((smb://)([^/]+)([^:]*))|((cifs://)([^/]+)([^:]*))|((http://)([^/][^/]*)([^:]*))|((https://)([^/][^/]*)([^:]*))|((file://)()([^:]*))|(()()([^:]*)))[:]*"
)
_COMPI = [
    3,
    7,
    11,
    15,
    19,
    23,
]


def net_normpathx(path, **kargs):
    """Extends 'os.path.normpathx' for network filesystems applications.

    .. warning::

       This module is currently an experimental release for discussion 
       and may change. Do not use it in production code!

    The basic extension is the split of the full application level pathname
    into it's application parts and the actual pathname of the node. The 
    pathname of the node is still passed onto the call 'os.path.normpath',
    with a few exceptions only, whereas the network application part, and/or
    eventual protocol key of the URI are handled separately.

    Thus the behavior for the filesystem address - the local path almost
    remains, while is extended by a network portion.

    But due to the eventual different remote filesystem attributes the local
    evaluation remains unsafe, while else requires remote access for assurance
    of the parameters.

    Args:
        plist: List of paths to be cleared.
            See common options for details.

            default := sys.path

        **kargs:
            fstype: The type of the final target filesystem.
                This is required because a remote filesystem 
                could be 's.th.' completely different, e.g.
                just a virtual representation of anything.

                default := <local-filesystem-type>

            raw: Suppress of the call of 'os.path.normpath' and
                the generic term 'share'.

    Returns:
        When successful returns the split file pathname, else returns 
        either 'None', or raises an exception.

    Raises:
        passed through exceptions:
    """
    _fstype = False
    _raw = False

    for k, v in kargs.items():
        if k == 'fstype':
            _fstype = v
        elif k == 'raw':
            _raw = v

    def clearp(p):
        p = p[1:].lstrip(os.sep)
        return p

    for i in _COMP.finditer(path):
        for g in _COMPI:
            if i.group(g):  # a uri
                # returns one only
                return (i.group(g)[:-3], i.group(g + 1),
                        clearp(i.group(g + 2)))
            elif i.group(g + 2):  # the local filesystem
                # returns one only
                return (i.group(g)[:-3], i.group(g + 1),
                        clearp(i.group(g + 2)))
    return None
