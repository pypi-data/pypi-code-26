from fedoidcmsg.entity import make_federation_entity
from oidcmsg.key_jar import init_key_jar
from oidcrp import RPHandler

__version__ = '0.1.1'


class FedRPHandler(RPHandler):
    def __init__(self, base_url='', hash_seed="", keyjar=None, verify_ssl=True,
                 services=None, service_factory=None, client_configs=None,
                 client_authn_factory=None, client_cls=None,
                 state_db=None, rp_config=None, **kwargs):
        RPHandler.__init__(self,base_url, hash_seed, keyjar, verify_ssl,
                           services, service_factory, client_configs,
                           client_authn_factory, client_cls, state_db, **kwargs)

        self.federation_entity = make_federation_entity(
            rp_config['federation'], '')

        self.jwks_uri_path = rp_config['jwks']['public_path']
        self.keyjar = init_key_jar(**rp_config['jwks'])
