import os
import sys
import time
import shutil
import asyncio
import zipfile
import logging
import tempfile
import subprocess
import requests

from twisted.internet import asyncioreactor
asyncioreactor.install()
from twisted.internet import defer
from twisted.python import log as twisted_log
twisted_log.PythonLoggingObserver().start()

from electrumx.server.controller import Controller
from electrumx.server.env import Env
from lbryumx.coin import LBCRegTest as XLBCRegTest
from lbrynet.wallet import LBCRegTest
from torba.wallet import Wallet, Account
from lbrynet.wallet import LbryWalletManager



root = logging.getLogger()
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


class BaseLbryServiceStack:

    def __init__(self, verbose=False):
        defer.setDebugging(verbose)
        logging.getLogger('lbryumx').setLevel(logging.INFO)
        logging.getLogger('electrumx').setLevel(logging.INFO)
        logging.getLogger('twisted').setLevel(logging.INFO)
        self.lbrycrd = Lbrycrd(verbose=verbose)
        self.server = LbryServer(self.lbrycrd)

    async def startup(self, before_lbrycrd_start=None, after_lbrycrd_start=None):
        self.lbrycrd.setup()
        if before_lbrycrd_start:
            await before_lbrycrd_start()
        await self.lbrycrd.start()
        if after_lbrycrd_start:
            await after_lbrycrd_start()
        else:
            await self.lbrycrd.generate(110)
        await self.server.start()

    async def shutdown(self, cleanup=True):
        try:
            await self.server.stop(cleanup=cleanup)
        except Exception as e:
            print(e)

        try:
            await self.lbrycrd.stop(cleanup=cleanup)
        except Exception as e:
            print(e)


class LbryServiceStack(BaseLbryServiceStack):

    def __init__(self, verbose=False):
        super().__init__(verbose)
        self.wallet = LbryWallet(verbose=verbose)

    async def startup(self, before_lbrycrd_start=None, after_lbrycrd_start=None):
        await super().startup(before_lbrycrd_start, after_lbrycrd_start)
        await self.wallet.start()

    async def shutdown(self, cleanup=True):
        try:
            await self.wallet.stop(cleanup=cleanup)
        except Exception as e:
            print(e)
        await super().shutdown(cleanup)


class LbryWallet:

    def __init__(self, verbose=False, profiler=None):
        self.verbose = verbose
        self.data_path = None
        self.wallet_directory = None
        self.download_directory = None
        self.profiler = profiler
        self.manager = LbryWalletManager()
        ledger = self.manager.get_or_create_ledger(
            LBCRegTest.get_id(), {
                'default_servers': [('localhost', 1984)],
            }
        )
        coin = LBCRegTest(ledger)
        self.wallet = Wallet('Main', [coin], [Account.generate(coin, u'lbryum')])
        self.manager.wallets.append(self.wallet)

    async def start(self):
        self.data_path = tempfile.mkdtemp()
        self.wallet_directory = os.path.join(self.data_path, 'lbryum')
        os.mkdir(self.wallet_directory)
        with open(os.path.join(self.wallet_directory, 'regtest_headers'), 'w'):
            pass
        await self.manager.start().asFuture(asyncio.get_event_loop())

    async def stop(self, cleanup=True):
        try:
            await self.manager.stop().asFuture(asyncio.get_event_loop())
        finally:
            if cleanup:
                self.cleanup()

    def cleanup(self):
        shutil.rmtree(self.data_path, ignore_errors=True)


class LbryServer:

    def __init__(self, lbrycrd):
        self.lbrycrd = lbrycrd
        self.controller = None
        self.data_path = None

    @property
    def lbryum_conf(self):
        return os.path.join(self.data_path, 'lbryum.conf')

    async def load_up_claims(self, claims):
        session = next(iter(self.controller.sessions))
        block_hashes = await session.daemon.generate(110)
        for name, hexvalue in claims:
            await session.daemon.claimname(name, hexvalue, 0.001)
            block_hashes.extend(await session.daemon.generate(1))
        raw_blocks = await session.daemon.raw_blocks(block_hashes)
        await session.daemon.height()  # just to load up the cached height
        blocks = [XLBCRegTest.block(raw_block, i) for (i, raw_block) in enumerate(raw_blocks, start=0)]
        session.bp.advance_blocks(blocks)

    async def start(self):
        self.data_path = tempfile.mkdtemp()
        conf = {
            'DB_DIRECTORY': self.data_path,
            'DAEMON_URL': 'http://rpcuser:rpcpassword@localhost:50001/',
            'REORG_LIMIT': '100',
            'TCP_PORT': '1984'
        }
        os.environ.update(conf)
        self.controller = Controller(Env(XLBCRegTest))
        self.controller.start_time = time.time()
        await self.controller.start_servers()
        await self.controller.tcp_server_started.wait()

    async def stop(self, cleanup=True):
        try:
            await self.controller.shutdown()
        finally:
            if cleanup:
                self.cleanup()

    def cleanup(self):
        shutil.rmtree(self.data_path, ignore_errors=True)


class LbrycrdProcess(asyncio.SubprocessProtocol):

    IGNORE_OUTPUT = [
        b'keypool keep',
        b'keypool reserve',
        b'keypool return',
    ]

    def __init__(self, verbose=False):
        self.ready = asyncio.Event()
        self.stopped = asyncio.Event()
        self.verbose = verbose

    def pipe_data_received(self, fd, data):
        if self.verbose and not any(ignore in data for ignore in self.IGNORE_OUTPUT):
            print(data.decode('ascii'))
        if b'Error:' in data:
            self.ready.set()
            raise SystemError(data.decode('ascii'))
        elif b'Done loading' in data:
            self.ready.set()
        elif b'Shutdown: done' in data:
            self.stopped.set()

    def process_exited(self):
        self.stopped.set()


class Lbrycrd:

    def __init__(self, parent_path=None, bin_path=None, verbose=False):
        self.parent_data_path = parent_path
        self.data_path = None
        self.project_dir = os.path.dirname(os.path.dirname(__file__))
        self.lbrycrd_dir = bin_path or os.path.join(self.project_dir, 'bin')
        self.lbrycrd_zip = 'lbrycrd-linux.zip'
        self.zip_path = os.path.join(self.lbrycrd_dir, self.lbrycrd_zip)
        self.lbrycrd_cli_path = os.path.join(self.lbrycrd_dir, 'lbrycrd-cli')
        self.lbrycrdd_path = os.path.join(self.lbrycrd_dir, 'lbrycrdd')
        self.verbose = verbose
        self.protocol = None
        self.transport = None

    @property
    def exists(self):
        return (
            os.path.exists(self.lbrycrdd_path) and
            os.path.exists(self.lbrycrd_cli_path)
        )

    @property
    def latest_release_url(self):
        r = requests.get('https://api.github.com/repos/lbryio/lbrycrd/releases/latest')
        d = r.json()
        for asset in d['assets']:
            if self.lbrycrd_zip in asset['browser_download_url']:
                return asset['browser_download_url']

    def download(self):
        if not os.path.exists(self.lbrycrd_dir):
            os.mkdir(self.lbrycrd_dir)
        r = requests.get(self.latest_release_url, stream=True)
        with open(self.zip_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        with zipfile.ZipFile(self.zip_path) as zf:
            zf.extractall(self.lbrycrd_dir)
        # zipfile bug https://bugs.python.org/issue15795
        os.chmod(self.lbrycrd_cli_path, 0o755)
        os.chmod(self.lbrycrdd_path, 0o755)
        return True

    def ensure(self):
        return self.exists or self.download()

    @property
    def lbrycrd_conf(self):
        return os.path.join(self.data_path, 'lbrycrd.conf')

    def setup(self):
        self.ensure()
        self.data_path = tempfile.mkdtemp()
        with open(self.lbrycrd_conf, 'w') as conf:
            conf.write(
                'rpcuser=rpcuser\n'
                'rpcpassword=rpcpassword\n'
                'rpcport=50001\n'
            )

    async def start(self):
        loop = asyncio.get_event_loop()
        asyncio.get_child_watcher().attach_loop(loop)
        self.transport, self.protocol = await loop.subprocess_exec(
            lambda: LbrycrdProcess(self.verbose),
            self.lbrycrdd_path,
            '-datadir={}'.format(self.data_path),
            '-printtoconsole', '-regtest', '-server', '-txindex',
        )
        await self.protocol.ready.wait()

    async def stop(self, cleanup=True):
        try:
            self.transport.terminate()
            await self.protocol.stopped.wait()
        finally:
            if cleanup:
                self.cleanup()

    def cleanup(self):
        shutil.rmtree(self.data_path, ignore_errors=True)

    async def _cli_cmnd(self, *args):
        cmnd_args = [
            self.lbrycrd_cli_path, '-datadir={}'.format(self.data_path), '-regtest',
        ] + list(args)
        self.verbose and print(' '.join(cmnd_args))
        loop = asyncio.get_event_loop()
        asyncio.get_child_watcher().attach_loop(loop)
        process = await asyncio.create_subprocess_exec(
            *cmnd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        out, err = await process.communicate()
        self.verbose and print(out.decode().strip())
        return out.decode().strip()

    def generate(self, blocks):
        return self._cli_cmnd('generate', str(blocks))

    def sendtoaddress(self, address, credits):
        """ Returns the transaction id. """
        return self._cli_cmnd('sendtoaddress', address, str(credits))

    def sendrawtransaction(self, tx):
        return self._cli_cmnd('sendrawtransaction', tx.decode())

    def decoderawtransaction(self, tx):
        return self._cli_cmnd('decoderawtransaction', tx.decode())

    def getrawtransaction(self, txid):
        return self._cli_cmnd('getrawtransaction', txid, '1')

    def claimname(self, name, value, amount):
        return self._cli_cmnd('claimname', name, value, str(amount))
