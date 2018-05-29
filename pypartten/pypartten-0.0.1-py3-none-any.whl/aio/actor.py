import abc
import asyncio


class ActorExit(Exception):
    pass

class ActorClosing(Exception):
    pass


class InboxFull(Exception):
    pass


class ActorMixinAbc(abc.ABC):
    """actor模型的混入基类.

    actor模型是一个并发模型,它通过自己维护一个邮箱来接收消息执行操作.
    将其定义为Mixin是因为它是一种行为模式,可以嵌入其他类中.满足下面的接口都可以是actor.

    通常actor模型不会单独使用,而是结合发布订阅模式做广播,结合中介模式做点对点通信.

    publish:
        inbox (asyncio.Queue): 邮箱,即队列
        running (bool):状态标明是否在执行

    protected:
        _actor_task (asyncio.Task): ensure_future后的协程任务.


    abcmethod:
        receive (corfunc): 接收信息后的处理过程
    """

    def __init__(self, maxsize=10, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.inbox = asyncio.Queue(maxsize=maxsize, loop=self.loop)
        self.running = False
        self.closing = False
        self._actor_task = None


    async def send(self, msg):
        '''使用异步接口向自己的邮箱发送消息.'''
        if self.closing is True:
            raise ActorClosing("is closing, no recive new message any more")
        else:
            try:
                await self.inbox.put(msg)
            except asyncio.queues.QueueFull as qf:
                raise InboxFull("邮箱满了")

    async def send_until_success(self, msg):
        ''''发送消息直到消息被接收'''
        while True:
            try:
                await self._send(msg)
            except InboxFull as full:
                continue
            else:
                break

    async def close(self):
        """关闭actor协程.注意不是立刻关闭,而是将队列中都执行完毕再关闭."""
        self.closing = True
        await self.send_until_success(ActorExit)


    async def handle_timeout(self):
        pass

    async def process(self):
        self.running = True
        while self.running:
            try:
                message = await self.inbox.get()
            except asyncio.TimeoutError:
                await self.handle_timeout()
            except asyncio.queues.QueueEmpty:
                continue
            else:
                if message is ActorExit:
                    print("actor closed")
                    self.running = False
                    asyncio.Task.current_task().cancel()
                    #raise ActorExit()
                else:
                    await self.receive(message)

    def run(self):
        self._actor_task = asyncio.ensure_future(self.process())

    @abc.abstractmethod
    async def receive(self, message):
        """需要实现的receive方法."""
        raise NotImplemented()
    