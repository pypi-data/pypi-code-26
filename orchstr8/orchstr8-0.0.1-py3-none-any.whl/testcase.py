import asyncio
from twisted.trial import unittest
from twisted.internet import utils, defer
from twisted.internet.utils import runWithWarningsSuppressed as originalRunWith
from orchstr8.services import LbryServiceStack
from orchstr8.fixture import Fixture


class IntegrationTestCase(unittest.TestCase):

    VERBOSE = False
    USE_FIXTURE = False

    async def setUp(self):
        self.service = LbryServiceStack(self.VERBOSE)
        await self.service.startup(self.setUpFixture, self.setUpLbrycrd)

    async def setUpFixture(self):
        """ Called before lbrycrd is started to extract a fresh
            blockchain fixture. May return Deferred."""
        if self.USE_FIXTURE:
            fixture = Fixture()
            fixture.lbrycrd = self.service.lbrycrd
            fixture.extract()

    async def setUpLbrycrd(self):
        """ Called after lbrycrd is started to do any further setup
            before starting lbryum-server. May return Deferred. """
        if not self.USE_FIXTURE:
            await self.service.lbrycrd.generate(110)

    async def tearDown(self):
        await self.service.shutdown()

    @property
    def lbrycrd(self):
        return self.service.lbrycrd

    @property
    def server(self):
        return self.service.server

    @property
    def manager(self):
        return self.service.wallet.manager

    @property
    def wallet(self):
        return self.service.wallet.wallet


def run_with_async_support(suppress, f, *a, **kw):
    if asyncio.iscoroutinefunction(f):
        def test_method(*args, **kwargs):
            return defer.Deferred.fromFuture(asyncio.ensure_future(f(*args, **kwargs)))
    else:
        test_method = f
    return originalRunWith(suppress, test_method, *a, **kw)


utils.runWithWarningsSuppressed = run_with_async_support
