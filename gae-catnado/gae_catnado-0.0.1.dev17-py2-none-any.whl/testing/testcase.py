import unittest

from google.appengine.ext import testbed


class SimpleAppEngineTestCase(unittest.TestCase):
  """A very simple AppEngine test case which sets up basic stubs.

  By default, stubs for Datastore and Memcache are created.
  """

  def setUp(self):
    """Override setUp to set up stubs."""
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()

  def tearDown(self):
    """Override tearDown to set up stubs."""
    self.testbed.deactivate()
