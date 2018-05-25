import asyncio
import logging

from aioamqp.exceptions import AioamqpException
from sage_utils.amqp.base import AmqpWorker
from sage_utils.amqp.clients import RpcAmqpClient


LOGGER = logging.getLogger(__name__)


class BaseRegisterWorker(AmqpWorker):
    """
    Base class for implementing worker which is registering a new
    microservice in Open Matchmaking platform.
    """
    MAX_RETRIES = 5
    RETRY_TIMEOUT = 10

    REQUEST_QUEUE_NAME = "auth.microservices.register"
    REQUEST_EXCHANGE_NAME = "open-matchmaking.direct"
    RESPONSE_EXCHANGE_NAME = "open-matchmaking.responses.direct"
    CONTENT_TYPE = 'application/json'

    def get_microservice_data(self, app):
        raise NotImplementedError("The `get_microservice_data(data)` method "
                                  "must be implemented.")

    async def run(self, *args, **kwargs):
        client = RpcAmqpClient(
            self.app,
            routing_key=self.REQUEST_QUEUE_NAME,
            request_exchange=self.REQUEST_EXCHANGE_NAME,
            response_queue='',
            response_exchange=self.RESPONSE_EXCHANGE_NAME
        )

        is_registered = False
        microservice_data = self.get_microservice_data(self.app)
        for _ in range(self.MAX_RETRIES):
            try:
                response = await client.send(
                    payload=microservice_data,
                    consume_timeout=self.RETRY_TIMEOUT
                )

                if 'error' in response.keys():
                    LOGGER.error("Received validation errors: {}".format(response['error']))
                else:
                    assert 'content' in response.keys()
                    assert response['content'] == 'OK'
                    is_registered = True

                break
            except (AioamqpException, TimeoutError):
                LOGGER.error(
                    "Can't receive a response because the Auth/Auth microservice isn't "
                    "responding or the required queues and the exchanges aren't created. "
                    "Retry after {} second(s).".format(self.RETRY_TIMEOUT)
                )
                await asyncio.sleep(self.RETRY_TIMEOUT, loop=self.app.loop)

        if not is_registered:
            raise ConnectionError('Occurred an error during registering microservice.')
