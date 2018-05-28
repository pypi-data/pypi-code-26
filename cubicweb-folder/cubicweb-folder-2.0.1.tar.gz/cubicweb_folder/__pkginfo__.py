# pylint: disable-msg=W0622
"""cubicweb-classification-folder packaging information"""

modname = 'cubicweb_folder'
distname = "cubicweb-folder"

numversion = (2, 0, 1)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://www.cubicweb.org/project/%s' % distname
description = "folder component for the CubicWeb framework"
classifiers = [
           'Environment :: Web Environment',
           'Framework :: CubicWeb',
           'Programming Language :: Python',
           'Programming Language :: JavaScript',
           ]

__depends__ = {'cubicweb': '>= 3.24.0',
               'six': '>= 1.4.0', }

__recommends__ = {}
