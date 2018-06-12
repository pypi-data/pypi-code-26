"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.brew.base import Brew
from pubkeeper.protocol.v1.protocol import PubkeeperProtocol
from pubkeeper.protocol.v1.brewer.brewer import ProtocolBrewer
from pubkeeper.protocol.v1.patron.patron import ProtocolPatron
from pubkeeper.protocol.v1.packet import (
    Packet,
    ClientAuthenticatePacket, SegmentRegisterPacket,
    BrewsRegisterPacket, BrewerRegisterPacket,
    BrewerUnregisterPacket, PatronRegisterPacket,
    PatronUnregisterPacket, BrewsStatePacket
)
from pubkeeper.protocol.v1.segment.manager import SegmentManager
from pubkeeper.utils.exceptions import (
    UnauthenticatedException, NoProtocolError
)
from tornado import gen
from tornado.locks import Event
from threading import RLock


class ClientProtocolHandler(PubkeeperProtocol):
    def __init__(self, client, selected_protocol=None):
        super().__init__()
        self._client = client
        self._authenticated_event = Event()

        self.selected_protocol = selected_protocol

        self._brews_state = {}

        self._data_lock = RLock()

        self.handlers.update({
            Packet.CLIENT_AUTHENTICATED: self.on_client_authenticated,
            Packet.BREWER_NOTIFY: self.on_brewer_notify,
            Packet.BREWER_REMOVED: self.on_brewer_removed,
            Packet.PATRON_NOTIFY: self.on_patron_notify,
            Packet.PATRON_REMOVED: self.on_patron_removed,
            Packet.SEGMENT_CREATE: self.on_segment_create,
            Packet.SEGMENT_DESTROY: self.on_segment_destroy,
            Packet.SEGMENT_CONNECT_BREWER: self.on_segment_connect_brewer,
        })

    @gen.coroutine
    def _on_connected(self, connection):
        self._connection = connection

        try:
            for brewer in self._client._brewers:
                self.remove_brewer(brewer, True)

            for patron in self._client._patrons:
                self.remove_patron(patron, True)
        except NoProtocolError:
            pass

        SegmentManager.reset()

        self._write_message(
            ClientAuthenticatePacket(token=self._client._config['token'])
        )

        yield self._authenticated_event.wait(
            timeout=self._client._io_loop.time() +
            self._client._config['authenticate_timeout']
        )

        if not self._client._authenticated:  # pragma no cover
            raise UnauthenticatedException()

        self.logger.info("Authenticated to Pubkeeper")

    def _on_disconnected(self):
        self._client._authenticated = False
        self._authenticated_event.clear()

    def write_message(self, msg):
        self._connection.write_message(msg, binary=True)

    # Function pointer mappings
    @staticmethod
    def get_brewer_functions():
        return {
            'configure': ProtocolBrewer.configure,
            'get_config': ProtocolBrewer.get_config,
            'new_patrons': ProtocolBrewer.new_patrons,
            'remove_patron': ProtocolBrewer.remove_patron,
            'brew': ProtocolBrewer.brew
        }

    @staticmethod
    def get_patron_functions():
        return {
            'configure': ProtocolPatron.configure,
            'new_brewers': ProtocolPatron.new_brewers,
            'remove_brewer': ProtocolPatron.remove_brewer,
            '_handle_callback': ProtocolPatron._handle_callback
        }

    # Protocol Handlers
    def on_client_authenticated(self, authenticated):
        if authenticated:
            self._client._authenticated = True
        else:
            self._client._authenticated = False

        self._authenticated_event.set()

    def on_brewer_notify(self, patron_id, brewers):
        with self._data_lock:
            for patron in [p for p in self._client._patrons
                           if p.patron_id == patron_id]:
                patron.new_brewers(brewers)

                if self._state_change_callback:
                    self._state_change_callback(Packet.BREWER_NOTIFY,
                                                patron)

    def on_brewer_removed(self, topic, patron_id, brewer_id):
        with self._data_lock:
            for patron in [p for p in self._client._patrons
                           if p.patron_id == patron_id]:
                patron.remove_brewer(brewer_id)

                if self._state_change_callback:
                    self._state_change_callback(Packet.BREWER_REMOVED,
                                                patron)

    def on_patron_notify(self, brewer_id, patrons):
        with self._data_lock:
            for brewer in [b for b in self._client._brewers
                           if b.brewer_id == brewer_id]:
                brewer.new_patrons(patrons)

                if self._state_change_callback:
                    self._state_change_callback(Packet.PATRON_NOTIFY,
                                                brewer)

    def on_patron_removed(self, topic, brewer_id, patron_id):
        with self._data_lock:
            for brewer in [b for b in self._client._brewers
                           if b.brewer_id == brewer_id]:
                brewer.remove_patron(patron_id)

                if self._state_change_callback:
                    self._state_change_callback(Packet.PATRON_REMOVED,
                                                brewer)

    def on_segment_create(self,
                          segment_id,
                          patron_details,
                          brewer_details):
        with self._data_lock:
            new_brewer_brew, new_patron_brew = \
                SegmentManager.create(self,
                                      segment_id,
                                      patron_details,
                                      brewer_details)

            self._write_message(
                SegmentRegisterPacket(segment_id,
                                      new_brewer_brew,
                                      new_patron_brew)
            )

    def on_segment_connect_brewer(self, segment_id, patron_id, patron_brew):
        with self._data_lock:
            SegmentManager.connect_brewer(segment_id, patron_id, patron_brew)

    def on_segment_destroy(self, segment_id):
        with self._data_lock:
            SegmentManager.destroy(segment_id)

    # Misc Callback Handler
    def _state_change_callback(self, act, obj):
        if 'state_change_callback' in self._client._config:
            self._client._config['state_change_callback'](act, obj)

    # Protocol Implementations
    def register_brews(self, brews, bridge_mode):
        with self._data_lock:
            self._registered_brews = brews
            self._bridge_mode = bridge_mode

            self._write_message(BrewsRegisterPacket(
                brews, bridge_mode
            ))

    def set_brew_state(self, brew, state):
        brew_name = brew.name if isinstance(brew, Brew) else brew
        self._brews_state[brew_name] = state

        self._write_message(BrewsStatePacket(
            brew_name, state
        ))

    def add_brewer(self, brewer):
        brew_configs = []
        brewer_config = brewer.get_config()

        with self._data_lock:
            for brew in brewer.brews:
                details = {'name': brew.name}
                brew_details = brew.create_brewer(brewer)
                if brew_details:
                    if not isinstance(brew_details, dict):  # pragma no cover
                        brew.destroy_brewer(brewer)
                        raise RuntimeError("Create Brewer returned a non dict")

                    details.update(brew_details)

                brew_configs.append(details)

        self._write_message(BrewerRegisterPacket(
            brewer.topic,
            brewer.brewer_id,
            brewer_config,
            brew_configs
        ))

    def remove_brewer(self, brewer, quiet=False):
        with self._data_lock:
            for brew in brewer.brews:
                brew.destroy_brewer(brewer)

        if not quiet:
            self._write_message(BrewerUnregisterPacket(
                brewer.topic,
                brewer.brewer_id
            ))

    def add_patron(self, patron):
        brew_configs = []

        with self._data_lock:
            for brew in patron.brews:
                details = {}
                details['name'] = brew.name
                brew_details = brew.create_patron(patron)
                if brew_details:  # pragma no cover
                    if not isinstance(brew_details, dict):
                        brew.destroy_patron(patron)
                        raise RuntimeError("Create Patron returned a non dict")

                    details.update(brew_details)

                brew_configs.append(details)

        self._write_message(PatronRegisterPacket(
            patron.topic,
            patron.patron_id,
            brew_configs
        ))

    def remove_patron(self, patron, quiet=False):
        with self._data_lock:
            for brew in patron.brews:
                brew.destroy_patron(patron)

        if not quiet:
            self._write_message(PatronUnregisterPacket(
                patron.topic,
                patron.patron_id
            ))
