import logging

from fedoidcmsg import ClientMetadataStatement
from fedoidcmsg import KeyBundle
from fedoidcmsg.utils import replace_jwks_key_bundle
from oidcendpoint import sanitize
from oidcendpoint.oidc import registration
from oidcmsg.oauth2 import ResponseMessage

logger = logging.getLogger(__name__)


class Registration(registration.Registration):

    @staticmethod
    def is_federation_request(req):
        if 'metadata_statements' in req or 'metadata_statement_uris' in req:
            return True
        else:
            return False

    def process_request(self, request=None, **kwargs):
        if not self.is_federation_request(request):
            return registration.Registration.process_request(self,
                                                             request.to_json(),
                                                             authn=None,
                                                             **kwargs)

        try:
            request.verify()
        except Exception as err:
            logger.exception(err)
            return ResponseMessage(error='Invalid request')

        logger.info(
            "registration_request:{}".format(sanitize(request.to_dict())))

        _fe = self.endpoint_context.federation_entity

        les = _fe.get_metadata_statement(request, context='registration')

        if les:
            ms = _fe.pick_by_priority(les)
            _fe.federation = ms.fo
        else:  # Nothing I can use
            return ResponseMessage(
                error='invalid_request',
                error_description='No signed metadata statement I could use')

        _pc = ClientMetadataStatement(**ms.protected_claims())

        if _pc:
            resp = self.client_registration_setup(_pc)
        else:
            resp = self.client_registration_setup(
                ms.unprotected_and_protected_claims())

        result = ClientMetadataStatement(**resp.to_dict())

        if 'signed_jwks_uri' in _pc:
            _kb = KeyBundle(source=_pc['signed_jwks_uri'],
                            verify_keys=ms.signing_keys,
                            verify_ssl=False)
            _kb.do_remote()
            replace_jwks_key_bundle(self.endpoint_context.keyjar,
                                    result['client_id'], _kb)
            result['signed_jwks_uri'] = _pc['signed_jwks_uri']

        result = _fe.update_metadata_statement(result, context='response')
        return {'response_args': result}
