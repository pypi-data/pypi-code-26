"""
Decorators module
"""
from .settings import URL, PORT, KEEPALIVE


def ensure_connection(func):
    """
    Decorator to ensure connection before execute any decorated method
    """
    def wrapper(self, *args, **kwargs):
        try:
            getattr(self, "connected")
        except AttributeError:
            self.connected = False
        finally:
            if not self.connected:
                self.connect(
                    self.url or URL,
                    self.port or PORT,
                    self.keepalive or KEEPALIVE
                )
                self.connected = True
        return func(self, *args, **kwargs)
    return wrapper
