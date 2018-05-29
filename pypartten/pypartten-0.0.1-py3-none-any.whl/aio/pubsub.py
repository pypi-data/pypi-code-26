import abc
from collections import defaultdict
from contextlib import contextmanager


class Publisher:
    """发布订阅模式.

    Exchange是一个发布器,会向所有发送者推送信息.

    protected:
        _subscribers (Set[]):订阅者,必须都有send()方法
    """

    def __init__(self):
        self._subscribers = set()

    def attach(self, subscriber):
        """订阅发布者."""
        self._subscribers.add(subscriber)

    def detach(self, subscriber):
        """取消订阅."""
        self._subscribers.remove(subscriber)

    @contextmanager
    def subscribe(self, *subscribers):
        """使用with语句订阅和取消订阅."""
        for subscriber in subscribers:
            self.attach(subscriber)
        try:
            yield self
        finally:
            for subscriber in subscribers:
                self.detach(subscriber)

    async def notify(self, msg):
        """向订阅者发送消息通知."""
        for subscriber in self._subscribers:
            await subscriber.send(msg)


_publishers = defaultdict(Publisher)


def get_publisher(name: str)->Publisher:
    return _publishers[name]


__all__ = ["get_publisher"]
