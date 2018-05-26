from asyncio import ensure_future

from aioamqp import connect as amqp_connect

from sage_utils.extension import BaseExtension


class AmqpExtension(BaseExtension):
    extension_name = 'amqp'
    app_attribute = 'amqp'
    workers = []
    active_tasks = []

    def register_worker(self, worker):
        self.workers.append(worker)

    def get_config(self, app):
        return {
            "login": app.config.get("AMQP_USERNAME", "guest"),
            "password": app.config.get("AMQP_PASSWORD", "guest"),
            "host": app.config.get("AMQP_HOST", "localhost"),
            "port": app.config.get("AMQP_PORT", 5672),
            "virtualhost": app.config.get("AMQP_VIRTUAL_HOST", "vhost"),
            "ssl": app.config.get("AMQP_USING_SSL", False),
        }

    async def connect(self):
        config = self.get_config(self.app)
        transport, protocol = await amqp_connect(**config)
        return transport, protocol

    async def init(self, loop):
        if not hasattr(self.app, 'extensions'):
            setattr(self.app, 'extensions', {})
        setattr(self.app, self.app_attribute, self)
        self.app.extensions[self.extension_name] = self

        for worker in self.workers:
            task = ensure_future(worker.run(), loop=loop)
            self.active_tasks.append(task)

    async def deinit(self, loop):
        for task in self.active_tasks:
            if not loop.is_closed and not task.cancelled():
                task.cancel()

        for worker in self.workers:
            await worker.free_resources()

        setattr(self.app, self.app_attribute, None)
        extensions = getattr(self.app, 'extensions', {})
        extensions.pop(self.extension_name, None)
