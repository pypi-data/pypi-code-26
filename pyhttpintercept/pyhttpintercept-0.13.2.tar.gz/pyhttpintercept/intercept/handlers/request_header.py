# encoding: utf-8

import logging_helper
from ._base import BaseInterceptHandler
from ...config.constants import HandlerTypeConstant

logging = logging_helper.setup_logging()


class InterceptHandler(BaseInterceptHandler):

    def handle_request(self,
                       request,
                       response,
                       client,
                       modifiers):

        """
        Called by HTTP_Web Server to handle a message.
        There should be no need to modify or override this.

        Filters modifiers so that only the ones appropriate
        to the message are applied.

        If there are no modifiers or a modifier fails to load,
        just returns the original response.
        """

        # logging.debug(u'in {name}.handle_response_headers'.format(name=self.__class__.__name__))

        headers = {}

        if self.can_you_handle(request):  # Shouldn't need this check, but worth leaving in

            # apply all modifications:
            for modifier in modifiers:
                logging.debug(modifier)

                # TODO: Write this.

        return headers
