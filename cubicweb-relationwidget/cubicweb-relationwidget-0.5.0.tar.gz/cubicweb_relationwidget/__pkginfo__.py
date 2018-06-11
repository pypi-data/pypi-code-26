# pylint: disable=W0622
"""cubicweb-relationwidget application packaging information"""

modname = 'cubicweb_relationwidget'
distname = 'cubicweb-relationwidget'

numversion = (0, 5, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'Provide a generic and ergonomic relation widget'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {'cubicweb': '>= 3.24.0',
               'cubicweb-bootstrap': '>= 1.2.0',
               'cwtags': '>= 0.1.1'}
__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]
