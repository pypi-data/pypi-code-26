class A:
    def func(self):
        print(self.__class__)
        pass


class B(A):
    def __init__(self):
        pass


b = B()
b.func()

a = A()
a.func()
