class Foo:
    def __init__(self):
        self._foo=5

    @property
    def foo(self):
        return self._foo

    @foo.setter
    def foo(self, value):
        print("setting")
        self._foo = value

f=Foo()
print(getattr(f, 'foo'))
setattr(f, 'foo', 50)
print(getattr(f, 'foo'))
