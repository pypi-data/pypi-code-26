from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.exception import ApplicationError
from autobahn.wamp.types import PublishOptions, SubscribeOptions, RegisterOptions
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import LoopingCall
from twisted.logger import Logger

import copy
import os
import time

RECEIVE_SESSION_REPORT = u'crossbarrelay.receive_session_report'
GET_SESSION_REPORTS = u'crossbarrelay.get_session_reports'

log = Logger()


def create_remote_session_class(relay, event_prefix=u''):
    class RemoteSession(ApplicationSession):
        def __init__(self, config):
            super(RemoteSession, self).__init__(config)

        def onJoin(self, details):
            self.log.info('Connected to remote router: {details}', details=details)
            self.subscribe(relay.on_remote_publish, event_prefix, options=SubscribeOptions(match=u'prefix', details_arg='details', get_retained=True))

            relay._remote_call = self.call
            relay.onRemoteJoin(details)

    return RemoteSession


class RelaySession(ApplicationSession):

    def __init__(self, config):
        super(RelaySession, self).__init__(config)
        self.event_prefix = config.extra['event_prefix']
        self.remote_router = config.extra['remote_router']
        self.remote_realm = config.extra['remote_realm']
        self.node_id = config.extra['id']

        self._remote_call = None

        if 'LIVETIMING_RELAY_KEY' not in os.environ:
            self.log.warn('LIVETIMING_RELAY_KEY not set, this relay will not be able to authenticate with the master')

    @inlineCallbacks
    def onJoin(self, details):
        self.log.info('Connected to local router: {details}', details=details)
        remote_session_class = create_remote_session_class(self, self.event_prefix)
        runner = ApplicationRunner(url=self.remote_router, realm=self.remote_realm)
        runner.run(remote_session_class, start_reactor=False, auto_reconnect=True)
        yield self.register(self.handle_rpc_call, self.event_prefix, RegisterOptions(match=u'prefix', details_arg='call_details'))

    def onRemoteJoin(self, details):
        LoopingCall(self.report_sessions).start(60)

    @inlineCallbacks
    def on_remote_publish(self, msg, details=None):
        self.log.debug("MSG: {msg} {details}", msg=msg, details=details)
        should_retain = details.retained or ("retain" in msg and msg['retain'])
        yield self.publish(details.topic, msg, options=PublishOptions(retain=should_retain))

    @inlineCallbacks
    def handle_rpc_call(self, *args, **kwargs):
        call_details = kwargs['call_details']
        self.log.debug('RPC request: args {args} call details {call_details}', args=args, call_details=call_details)
        result = yield self.remote_call(call_details.procedure, *args)
        returnValue(result)

    @inlineCallbacks
    def remote_call(self, proc, *args, **kwargs):
        if self._remote_call:
            result = yield self._remote_call(proc, *args, **kwargs)
            returnValue(result)

    @inlineCallbacks
    def report_sessions(self):
        try:
            sessions = yield self.call(u'wamp.session.count')
            yield self.remote_call(RECEIVE_SESSION_REPORT, self.node_id, sessions, os.environ.get('LIVETIMING_RELAY_KEY'))
        except ApplicationError:
            self.log.warn('Could not report statistics to remote router!')


def load_relay_keys(filename):
    keys = []
    try:
        with open(filename, 'r') as f:
            for line in f.readlines():
                if len(line.strip()) > 0 and line[0] != '#':
                    keys.append(line.strip())
    except IOError:
        log.warn('No keys file found at {filename}, no relays will be able to connect!', filename=filename)

    return keys


class RelayMonitor(ApplicationSession):
    log = Logger()
    THRESHOLD = 5 * 60  # Five minutes

    def __init__(self, config):
        super(RelayMonitor, self).__init__(config)
        self._reports = {}

    @inlineCallbacks
    def onJoin(self, details):
        yield self.register(self.get_session_reports, GET_SESSION_REPORTS)
        yield self.register(self.receive_session_report, RECEIVE_SESSION_REPORT)
        LoopingCall(self._cull_dead_relays).start(60)

    def get_session_reports(self):
        return self._reports

    def receive_session_report(self, node, session_count, relay_key):
        if relay_key in self._authorised_relay_keys():
            self._reports[node] = (session_count, time.time())
        else:
            self.log.warn('Received a session report from unauthorised relay {node} (using key:{key})', node=node, key=relay_key)

    def _cull_dead_relays(self):
        now = time.time()
        threshold = now - self.THRESHOLD
        for node, report in copy.copy(self._reports).iteritems():
            if report[1] < threshold:
                self.log.info("Node {node} has not reported for five minutes, removing from list", node=node)
                self._reports.pop(node)

    def _authorised_relay_keys(self):
        return load_relay_keys(os.environ.get('LIVETIMING_RELAY_KEY_FILE', 'relay-keys.txt'))
