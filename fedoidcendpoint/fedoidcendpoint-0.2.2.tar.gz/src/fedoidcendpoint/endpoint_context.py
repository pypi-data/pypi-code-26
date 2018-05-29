from fedoidcmsg.entity import make_federation_entity
from oidcendpoint import endpoint_context


class EndpointContext(endpoint_context.EndpointContext):
    def __init__(self, conf, keyjar=None, client_db=None, session_db=None,
                 cwd='', httpcli=None, verify_ssl=True):
        endpoint_context.EndpointContext.__init__(
            self, conf, keyjar=keyjar, client_db=client_db,
            session_db=session_db, cwd=cwd)

        self.federation_entity = make_federation_entity(conf['federation'],
                                                        conf['issuer'],
                                                        httpcli=httpcli,
                                                        verify_ssl=verify_ssl)
