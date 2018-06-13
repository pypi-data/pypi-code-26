import doctest
import os
import re
import unittest
from pkg_resources import resource_listdir

from zope.testing import cleanup, renormalizing
import zope.component.eventtesting

import grokcore.view
from grokcore.view.templatereg import file_template_registry

optionflags = (
    doctest.NORMALIZE_WHITESPACE +
    doctest.ELLIPSIS +
    renormalizing.IGNORE_EXCEPTION_MODULE_IN_PYTHON2
)


def setUp(test):
    zope.component.eventtesting.setUp(test)
    file_template_registry.ignore_templates('.svn')


def cleanUp(test):
    cleanup.cleanUp()

checker = renormalizing.RENormalizing([
    # str(Exception) has changed from Python 2.4 to 2.5 (due to
    # Exception now being a new-style class).  This changes the way
    # exceptions appear in traceback printouts.
    (re.compile(
        r"ConfigurationExecutionError: <class '([\w.]+)'>:"),
        r'ConfigurationExecutionError: \1:'), ])


def suiteFromPackage(name):
    layer_dir = 'base'
    files = resource_listdir(__name__, '{}/{}'.format(layer_dir, name))
    suite = unittest.TestSuite()
    for filename in files:
        if filename.endswith('_fixture.py'):
            continue
        if filename == '__init__.py':
            continue
        test = None
        if filename.endswith('.py'):
            dottedname = 'grokcore.view.tests.%s.%s.%s' % (
                layer_dir, name, filename[:-3])
            test = doctest.DocTestSuite(
                dottedname,
                setUp=setUp,
                tearDown=cleanUp,
                checker=checker,
                optionflags=optionflags)
        elif filename.endswith('.txt'):
            test = doctest.DocFileSuite(
                os.path.join(layer_dir, name, filename),
                optionflags=optionflags,
                setUp=setUp,
                tearDown=cleanUp,
                globs={'grok': grokcore.view})
        if test is not None:
            suite.addTest(test)
    return suite


def test_suite():
    suite = unittest.TestSuite()
    for name in [
            'contentprovider',
            'directoryresource',
            'skin',
            'template',
            'view']:
        suite.addTest(suiteFromPackage(name))
    suite.addTest(doctest.DocFileSuite(
        '../templatereg.txt',
        optionflags=optionflags,
        setUp=setUp,
        tearDown=cleanUp,
        # `checker` is not an officially supported options but it will be
        # forwarded as **kw to the DocTestCase.
        checker=checker,
        ))
    return suite
