

class AmqpWorker(object):

    def __init__(self, app, *args, **kwargs):
        self.app = app
        self.protocol = None
        self.transport = None

    async def run(self, *args, **kwargs):
        raise NotImplementedError('`run(*args, **kwargs)` method must be implemented.')

    async def connect(self):
        self.transport, self.protocol = await self.app.amqp.connect()
        return self.transport, self.protocol

    async def free_resources(self):
        if self.protocol:
            if not self.protocol.worker.cancelled():
                self.protocol.worker.cancel()

            await self.protocol.close()

        if self.transport:
            self.transport.close()

        self.transport = None
        self.protocol = None
