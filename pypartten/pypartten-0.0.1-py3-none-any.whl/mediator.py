from typing import (
    Any
)


class MediatorLabelUsed(Exception):
    pass


class Mediator:
    """中介模式.

    中介模式是用来解除独立对象间复杂交互的问题的.其核心思想是每个对象只要在其中注册,就可以通过它来找到要访问的对象从而实现解耦.

    作为中介,它最主要的工作是撮合,即如何找到要匹配的对象,因此有3个接口必不可少

    + 注册(regist)
    + 注销(logout)
    + 请求(query)

    注册的话为了方便中介查找,可以为注册的对象设置标签,查找的时候也就只需要查找标签即可.

    在python中我们完全可以使用dict结合模块只加载一次的特性使用常量来替代中介.
    而这个类的意义在于可以继承和扩展.
    """

    _mediator_table = {}

    def regist(self,label: str, obj: Any):
        if label in list(self._mediator_table.keys()):
            raise MediatorLabelUsed(f"label {label} used, find a new one")
        else:
            self._mediator_table[label] = obj

    def logout(self,obj):
        target = []
        for i,v in self._mediator_table.items():
            if v is obj:
                target.append(i)
        for i in target:
            del self._mediator_table[i]

    def query(self,label):
        return self._mediator_table.get(label)