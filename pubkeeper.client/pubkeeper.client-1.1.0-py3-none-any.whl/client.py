"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
import pubkeeper.protocol
from pubkeeper.brewer import Brewer, BrewerFT
from pubkeeper.patron import Patron, PatronFT
from pubkeeper.brew.brew_state import BrewState
from pubkeeper.utils.logging import get_logger
from pubkeeper.utils.websocket import WebsocketConnection
from pubkeeper.utils.exceptions import UnauthenticatedException
from tornado import ioloop, gen
from threading import Thread, RLock, Event
from pkgutil import iter_modules
from importlib import import_module


class PubkeeperClient(object):
    _AUTHENTICATE_TIMEOUT = 2
    _CLIENT_READY_TIMEOUT = 2

    def __init__(self, config=None, **kwargs):
        self.logger = get_logger('pubkeeper.client')
        self.protocol = None

        self._config = config

        if 'authenticate_timeout' not in self._config:
            self._config['authenticate_timeout'] = \
                self.__class__._AUTHENTICATE_TIMEOUT

        if 'jwt' in kwargs:
            self.logger.warn("Deprecated: Passing authentication token by "
                             "way of `jwt` argument to constructor will be "
                             "removed in a future version.  It should be "
                             "included as the `token` element to the config "
                             "given to this constructor")
            self._config['token'] = kwargs.pop('jwt')

        self._brews = []
        self._brewers = []
        self._patrons = []

        self._client_lock = RLock()

        self._io_loop = ioloop.IOLoop()

        self._established_protocol = None
        self._supported_protocols = {}
        self._load_protocol_modules()

        self._authenticated = False
        self._async = True

        self._bridge_mode = self._config.pop('bridge_mode', False)

        # Application Event Handlers
        self._app_on_connected = []
        self._app_on_disconnected = []

        versions = ['pubkeeper-{}'.format(p) for
                    p in self._supported_protocols.keys()]
        self._config['headers'] = versions

    def _load_protocol_modules(self):
        for _, modname, _ in iter_modules(
            path=pubkeeper.protocol.__path__,
            prefix=pubkeeper.protocol.__name__ + '.'
        ):
            try:
                constant = import_module(modname + ".constant")
            except ImportError:  # pragma no cover
                self.logger.warn(
                    "Installed {} has no constant "
                    "in this client version, skipping".format(modname)
                )
                continue

            try:
                handler = import_module(modname + ".handler")
            except ImportError:  # pragma no cover
                self.logger.warn(
                    "Installed {} has no handler "
                    "in this client version, skipping".format(modname)
                )
                continue

            if hasattr(constant, 'supported_protocol_versions'):
                for version in constant.supported_protocol_versions:
                    self._supported_protocols[version] = handler
            else:
                self._supported_protocols[constant.protocol_version] = handler

    def start(self, *args, _async=None, **kwargs):  # noqa
        if len(args):
            # assume bridge_mode was specified
            self.logger.warn("Deprecated: passing `bridge_mode` argument to "
                             "start will be removed in a future version. "
                             "`bridge_mode` should be defined in the config "
                             "passed to the constructor.")
            self._bridge_mode = args[0]
        if _async is None:
            self.logger.warn("Deprecated: No `_async` argument was given to "
                             "start.  This version will operate in a more "
                             "synchronous method, future versions will default "
                             "to an asynchronous startup")
            self._async = False
        else:
            self._async = _async

        if not self._async:
            self._client_ready = Event()

        self._client_thread = Thread(target=self.run)
        self._client_thread.start()

        if not self._async:
            if not self._client_ready. \
                    wait(PubkeeperClient._CLIENT_READY_TIMEOUT):
                raise RuntimeError("Client not ready")

    def run(self):
        self._io_loop.make_current()

        self._connection_module = WebsocketConnection(
            self._config,
            on_connected=self._on_connected,
            on_message=self._on_message,
            on_disconnected=self._on_disconnected,
            on_selected_protocol=self._on_selected_protocol,
        )

        for brew in self._brews:
            self._io_loop.add_callback(brew.start)

        self.logger.info("Pubkeeper Client Running ({} brews started)".format(
            len(self._brews)
        ))

        self._io_loop.start()
        self._io_loop.close()

        self.logger.info("Pubkeeper Client Shutdown")

    def stop(self):
        self.logger.info("Pubkeeper Client Shutting Down")

        with self._client_lock:
            for brewer in self._brewers:
                self._io_loop.add_callback(self.remove_brewer, brewer)

            for patron in self._patrons:
                self._io_loop.add_callback(self.remove_patron, patron)

            for brew in self._brews:
                self._io_loop.add_callback(brew.stop)

        self._io_loop.stop()
        self._client_thread.join()

    def shutdown(self):
        self.logger.warn("Deprecated: The `shutdown` method has been "
                         "renamed `stop`")
        self.stop()

    # Client API
    def add_brew(self, brew):
        with self._client_lock:
            if [b for b in self._brews if b.name == brew.name]:
                raise RuntimeError("Attempting to add an existing brew")

            brew.brew_state_listener = self.brew_state
            self._brews.append(brew)

    def remove_brew(self, brew):
        with self._client_lock:
            if brew not in self._brews:
                raise RuntimeError("Attempting to remove a brew "
                                   "that was not added")

            self._brews.remove(brew)

    def add_brewer(self, topic, **kwargs):
        if isinstance(topic, Brewer):
            brewer = topic
            brewer._io_loop = self._io_loop
        else:
            brewer = Brewer(topic, io_loop=self._io_loop, **kwargs)

        authenticated = False

        with self._client_lock:
            brewer.brews = self._brews
            self._brewers.append(brewer)

            if self._authenticated:
                authenticated = True

        if authenticated:
            brewer.configure()
            self._io_loop.add_callback(self.protocol.add_brewer, brewer)

        return brewer

    def remove_brewer(self, brewer):
        with self._client_lock:
            try:
                self._brewers.remove(brewer)
            except ValueError:  # pragma no cover
                self.logger.exception("Could not remove brewer from list")
                return

            if self._authenticated:
                self._io_loop.add_callback(self.protocol.remove_brewer, brewer)

    def add_patron(self, topic, callback=None, **kwargs):
        if isinstance(topic, Patron):
            patron = topic
            patron._io_loop = self._io_loop
        else:
            if callback is None:
                raise RuntimeError("Can not add a patron without a callback")

            patron = Patron(topic, callback, io_loop=self._io_loop,
                            **kwargs)

        authenticated = False

        with self._client_lock:
            patron.brews = self._brews
            self._patrons.append(patron)

            if self._authenticated:
                authenticated = True

        if authenticated:
            patron.configure()
            self._io_loop.add_callback(self.protocol.add_patron, patron)

        return patron

    def remove_patron(self, patron):
        with self._client_lock:
            try:
                self._patrons.remove(patron)
            except ValueError:  # pragma no cover
                self.logger.exception("Could not remove patron from list")
                return

            if self._authenticated:
                self._io_loop.add_callback(self.protocol.remove_patron, patron)

    def add_on_connected(self, callback):
        if not callable(callback):
            self.logger.warn("On Connected Callback is not "
                             "callable {}".format(callback))
            return

        with self._client_lock:
            self._app_on_connected.append(callback)

    def add_on_disconnected(self, callback):
        if not callable(callback):
            self.logger.warn("On Disconnected Callback is not "
                             "callable {}".format(callback))
            return

        with self._client_lock:
            self._app_on_disconnected.append(callback)

    def is_connected(self):
        with self._client_lock:
            # Are you really "connected" in terms of the application
            # if you can't actually utilize the service?
            return self._authenticated

    # Connection Handlers
    @gen.coroutine
    def _on_connected(self, connection):
        self.logger.info(
            "Connected To Pubkeeper ({0})".format(self._established_protocol)
        )

        BrewerFT.set(self.protocol.get_brewer_functions())
        PatronFT.set(self.protocol.get_patron_functions())

        try:
            yield self.protocol._on_connected(connection)
        except UnauthenticatedException:
            BrewerFT.reset()
            PatronFT.reset()
            self.logger.error("Could not authenticate to Pubkeeper")
            return

        self._io_loop.add_callback(self.protocol.register_brews,
                                   [b.name for b in self._brews],
                                   self._bridge_mode)

        for brewer in self._brewers:
            brewer.configure()
            self._io_loop.add_callback(self.protocol.add_brewer, brewer)

        for patron in self._patrons:
            patron.configure()
            self._io_loop.add_callback(self.protocol.add_patron, patron)

        if not self._async:
            self._client_ready.set()

        with self._client_lock:
            for callback in self._app_on_connected:
                callback()

    def _on_disconnected(self):
        self.logger.info("Disconnected from Pubkeeper")

        BrewerFT.reset(['reset', 'brew'])
        PatronFT.reset(['reset', '_handle_callback'])

        self._established_protocol = None
        self.protocol._connection = None
        self.protocol._on_disconnected()

        if not self._async:
            self._client_ready.clear()

        with self._client_lock:
            for callback in self._app_on_disconnected:
                callback()

    def _on_message(self, msg):
        if self.protocol:
            self.protocol.on_message(msg)

    def _on_selected_protocol(self, selected_protocol_str):
        selected_protocol = \
            selected_protocol_str[selected_protocol_str.index('-')+1:]
        self.protocol_module = \
            self._supported_protocols[selected_protocol]

        with self._client_lock:
            self._established_protocol = selected_protocol
            self.protocol = self.protocol_module.ClientProtocolHandler(
                self, selected_protocol
            )

    # Management Tools
    def brew_state(self, brew, state):
        with self._client_lock:
            if not isinstance(state, BrewState):
                raise ValueError("Invalid Brew State specified")

            self._io_loop.add_callback(self.protocol.set_brew_state,
                                       brew, state)
