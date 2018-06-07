import logging

import fedoidcmsg

from oidcendpoint.oidc import provider_config
from oidcmsg import oidc

logger = logging.getLogger(__name__)


class ProviderConfiguration(provider_config.ProviderConfiguration):
    request_cls = oidc.Message
    response_cls = fedoidcmsg.ProviderConfigurationResponse
    request_format = ''
    response_format = 'json'
    endpoint_name = 'discovery'

    def __init__(self, endpoint_context, **kwargs):
        provider_config.ProviderConfiguration.__init__(self, endpoint_context, **kwargs)
        # self.pre_construct.append(self._pre_construct)
        self.post_construct.append(self.add_federation_context)

    def process_request(self, request=None, **kwargs):
        return {'response_args': self.endpoint_context.provider_info.copy()}

    def provider_info_with_signing_keys(self):
        _context = self.endpoint_context
        _fe = _context.federation_entity
        return _fe.add_signing_keys(
            oidc.ProviderConfigurationResponse(**_context.provider_info))

    def add_federation_context(self, response, request, endpoint_context,
                               federation=None, setup=None, **kwargs):
        """
        Collects metadata about this provider add signing keys and use the
        signer to sign the complete metadata statement.

        :param response:
        :param client_id:
        :param endpoint_context:
        :param fos: List of federation operators
        :param setup: Extra keyword arguments to be added to the provider info
        :return: Depends on the signer used
        """

        _context = self.endpoint_context
        _fe = _context.federation_entity

        if federation is None:
            try:
                federation = list(_fe.metadata_statements['discovery'].keys())
            except AttributeError:
                federation = _fe.fo_priority
            if not federation:
                # For the moment there is a difference between None
                # and []. Want None in this case.
                fos = None

        logger.info(
            'provider:{}, federation:{}, context:{}'.format(
                _context.issuer, federation, 'discovery'))

        # _resp = _fe.add_signing_keys(response)

        if setup:
            response.update(setup)

        resp = _fe.update_metadata_statement(response, context='discovery',
                                             federation=federation)
        return resp
