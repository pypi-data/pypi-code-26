

class SanicAmqpExtensionMixin(object):
    """Mixin class for compatibility with sanic-amqp-extension package."""
    async def deinit(self, *args, **kwargs):
        await self.free_resources(*args, **kwargs)
