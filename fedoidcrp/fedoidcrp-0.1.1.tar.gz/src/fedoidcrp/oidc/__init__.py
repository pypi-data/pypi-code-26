from fedoidcmsg.entity import make_federation_entity
from oidcrp import oidc


class RP(oidc.RP):
    def __init__(self, state_db, ca_certs=None, client_authn_factory=None,
                 keyjar=None, verify_ssl=True, config=None, client_cert=None,
                 httplib=None, services=None, service_factory=None):
        oidc.RP.__init__(self, state_db, ca_certs,
                               client_authn_factory=client_authn_factory,
                               keyjar=keyjar, verify_ssl=verify_ssl,
                               config=config, client_cert=client_cert,
                               httplib=httplib, services=services,
                               service_factory=service_factory)

        fe = make_federation_entity(config['federation'], '', self.http)
        self.service_context.federation_entity = fe