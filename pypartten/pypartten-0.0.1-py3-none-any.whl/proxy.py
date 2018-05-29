import abc

class Proxy:
    """代理.

    用于作为占位符,在初始化后本身没有任何功能,但为其指定一个被代理对象后就可以通过访问代理来访问对象的内容了.

    其意义在于
    1. 屏蔽对对象直接的写操作,避免对象被篡改
    2. 重写__getattr__以提供一定的访问控制
    """
    __slots__ = ('obj', '_callbacks')

    def __init__(self):
        self._callbacks = []
        self.initialize(None)

    def initialize(self, obj):
        self.obj = obj
        for callback in self._callbacks:
            callback(obj)

    def attach_callback(self, callback):
        self._callbacks.append(callback)
        return callback

    def __getattr__(self, attr):
        if self.obj is None:
            raise AttributeError('Cannot use uninitialized Proxy.')
        return getattr(self.obj, attr)

    def __setattr__(self, attr, value):
        if attr not in self.__slots__:
            raise AttributeError('Cannot set attribute on proxy.')
        return super().__setattr__(attr, value)