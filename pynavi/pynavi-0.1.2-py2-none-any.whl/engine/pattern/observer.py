# -*- coding: utf-8 -*-
# Author: sunguangran (sunguangran@daixiaomi.com)

"""观察者模式"""


class Observer(object):
    """观察者"""

    def action(self, data):
        raise NotImplementedError


class Subject(object):
    """主题"""

    def __init__(self, name):
        self._name = name
        self._observers = []

    @property
    def name(self):
        return self._name

    def attach(self, observer):
        """添加观察者"""
        if observer not in self._observers:
            self._observers.append(observer)

        return self

    def detach(self, observer):
        """移除观察者"""
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

        return self

    def receive(self, data):
        self.notify(data)

    def notify(self, data):
        """通知观察者"""
        for observer in self._observers:
            if not isinstance(observer, Observer):
                continue

            observer.action(data)


# Example usage #####################################################################################
class TestObserver1(Observer):

    def action(self, data):
        print('ob1: data %s' % data)


class TestObserver2(Observer):

    def action(self, data):
        print('ob2: data %s' % data)


def main():
    data1 = Subject('Data 1')

    ob1 = TestObserver1()
    ob2 = TestObserver2()

    data1.attach(ob1).attach(ob2)

    data1.receive(10)
    data1.receive(3)

    data1.detach(ob2)

    data1.receive(10)
    data1.receive(9)


if __name__ == '__main__':
    main()
