import inspect
import os
from abc import abstractmethod

from . import utils

Missing = object()


@utils.auto_str(__repr__=True)
class Resolver(utils.Loggable):
    """
    Examples:

        >>> resolver = Resolver()
        >>> str(resolver)
        'Resolver(default_override=False, ignore=set())'
    """
    def __init__(self, ignore=None, default_override=False, **kwargs):
        if ignore is not None and not isinstance(ignore, str) and not hasattr(ignore, '__iter__'):
            raise TypeError("Argument 'ignore' is expected to be None, str or iterable, but is {}".format(type(ignore)))
        if not isinstance(default_override, bool):
            raise TypeError("Argument 'default_override' is expected to be a boolean, but is {}".format(
                type(default_override)))
        self.ignore = set(utils.make_list(ignore or []))
        self.default_override = default_override

    def _make_ignore(self, cls):
        return self.ignore.union(utils.get_field_mro(cls, '__resolver_ignore__'))

    @abstractmethod
    def _resolve_arg(self, name, value, defaults, cls):
        raise NotImplementedError()  # pragma: no cover

    def _call_resolve_arg(self, name, value, defaults, cls):
        # We won't tamper with self and cls
        if name in {'self', 'cls'}:
            return value
        # We won't change any passed arguments
        if value is not Missing:
            return value
        # We return the default if any
        if not self.default_override and name in defaults:
            return defaults[name]
        # We will ignore any argument in the ignore list
        if name in self._make_ignore(cls):
            return Missing
        # ... Otherwise we will try to resolve the argument dynamically
        newval = self._resolve_arg(name, value, defaults, cls)
        if newval is Missing and name in defaults:
            return defaults[name]
        return newval

    def __call__(self, fun):
        # Returns the wrapper
        return self.resolve(fun, self._call_resolve_arg)

    @staticmethod
    def resolve(wrapped_fun, resolve_fun):
        def wrapper(*args, **kwargs):
            # Argument name-value pairs
            sig = inspect.getargspec(wrapped_fun)
            defaults = {}
            if sig.defaults is not None:
                defaults = {k: v for k, v in list(zip(sig.args[-len(sig.defaults):], sig.defaults))}
            named_args = list(zip(sig.args, args))
            unset = (set(sig.args) -
                     set([name for name, _ in named_args])
                     .union(set([name for name, _ in kwargs.items()])))
            for u in unset:
                kwargs[u] = Missing

            mclazz = utils.get_class_that_defined_method(wrapped_fun)

            def call_resolve(name, value):
                return resolve_fun(name, value, defaults, mclazz)

            # new args + kwargs to inject to wrapped function
            new_kwargs = {name: call_resolve(name, value) for name, value in named_args}
            new_kwargs.update({name: call_resolve(name, value) for name, value in kwargs.items()})

            # call with new kwargs (ignore missing ones)
            return wrapped_fun(**{k: v for k, v in new_kwargs.items() if v is not Missing})
        return wrapper


class ConstResolver(Resolver):
    """
    Example:

        >>> class C:
        ...     @ConstResolver('resolved')
        ...     def f1(self, a, b, c='default'):
        ...         return a, b, c
        ...
        ...     @ConstResolver('resolved', ignore='b')
        ...     def f2(self, a, b):
        ...         return a, b
        ...
        ...     @ConstResolver('resolved', default_override=True)
        ...     def f3(self, a, b='default'):
        ...         return a, b

        >>> dut = C()
        >>> dut.f1('passed')  # Replaces any missing args by the given constant. Defaults and passed args are untouched
        ('passed', 'resolved', 'default')

        >>> dut.f1(b='passed', c='passed')  # Keyword args work too
        ('resolved', 'passed', 'passed')

        >>> dut.f2(b='passed')  # Will work
        ('resolved', 'passed')

        >>> dut.f2()  # Will not work. b cannot be resolved because it is ignored
        Traceback (most recent call last):
        ...
        TypeError: f2() missing 1 required positional argument: 'b'

        >>> dut.f3()  # Argument b will be resolved instead of set to default because of override.
        ('resolved', 'resolved')
    """
    def __init__(self, constant, **kwargs):
        super().__init__(**kwargs)
        self.constant = constant

    def _resolve_arg(self, name, value, defaults, cls):
        return self.constant


class MapResolver(Resolver):
    """
    Examples:
        >>> class C:
        ...     @MapResolver(dict(service1="Service1", service2="Service2"))
        ...     def f1(self, service1, service2=None):
        ...         return service1, service2
        ...     @MapResolver(dict(service1="Service1", service2="Service2"), default_override=True)
        ...     def f2(self, service1, service2=None):
        ...         return service1, service2
        ...     @MapResolver(dict(service1="Service1", service2="Service2"), default_override=True)
        ...     def f3(self, service1, service2, service3):
        ...         return service1, service2, service3

        >>> dut = C()
        >>> dut.f1()  # Resolution via map
        ('Service1', None)

        >>> dut.f2()  # Resolution of service2 cause of default override
        ('Service1', 'Service2')

        >>> dut.f3()  # Resolution of service3 will fail
        Traceback (most recent call last):
        ...
        TypeError: f3() missing 1 required positional argument: 'service3'

    """
    def __init__(self, mapping, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(mapping, dict):
            raise TypeError("Argument 'mapping' is expected to be a dictionary, but is {}".format(type(mapping)))
        self.mapping = mapping

    def _resolve_arg(self, name, value, defaults, cls):
        return self.mapping.get(name, Missing)


class ChainResolver(Resolver):
    """
    Examples:

        >>> resolver = ChainResolver(MapResolver(dict(a='map')), ConstResolver('const'))
        >>> gap_resolver = ChainResolver(MapResolver(dict(a='map')), MapResolver(dict(b='map2')))
        >>> class C:
        ...     @resolver
        ...     def f1(self, a, b, c):
        ...         return a, b, c
        ...     @gap_resolver
        ...     def f2(self, a, b, c='default'):
        ...         return a, b, c
        ...     @gap_resolver
        ...     def f3(self, a, b, c):
        ...         return a, b, c

        >>> dut = C()
        >>> dut.f1(c='passed')  # Argument resolution: 'a' by MapResolver, Argument 'b' by ConstResolver
        ('map', 'const', 'passed')

        >>> dut.f2()
        ('map', 'map2', 'default')

        >>> dut.f3()
        Traceback (most recent call last):
        ...
        TypeError: f3() missing 1 required positional argument: 'c'
    """
    def __init__(self, *resolver, **kwargs):
        super().__init__(**kwargs)
        self.resolver = utils.make_list(resolver)
        for r in self.resolver:
            if not isinstance(r, Resolver):
                raise ValueError("Item of argument 'resolver' is expected to be of type 'Resolver', but is {}".format(
                    type(r)))

    def _resolve_arg(self, name, value, defaults, cls):
        for r in self.resolver:
            res = r._resolve_arg(name, value, defaults, cls)
            if res is not Missing:
                return res
        return Missing


class EnvironmentResolver(Resolver):
    """
    Examples:

        >>> class C:
        ...     @EnvironmentResolver()
        ...     def login(self, password, username='user'):
        ...         return username, password
        ...     @EnvironmentResolver(prefix='pre', default_override=True)
        ...     def login2(self, username='user', password='broken'):
        ...         return username, password

        >>> dut = C()
        >>> with utils.modified_environ(PASSWORD='secret'):
        ...     dut.login()  # Resolution of argument 'password' via environment 'PASSWORD', default of 'username'
        ('user', 'secret')

        >>> with utils.modified_environ(PASSWORD='secret', USERNAME='admin'):
        ...     dut.login()  # No override of argument username's default
        ('user', 'secret')

        >>> with utils.modified_environ(PRE_USERNAME='admin'):
        ...     dut.login2()  # Resolution via prefix: Lookup is environment variable PRE_USERNAME; with override
        ('admin', 'broken')

        >>> with utils.modified_environ(PRE_USERNAME='admin', PRE_PASSWORD='secret'):
        ...     dut.login2()  # Override the default value of both arguments
        ('admin', 'secret')

    """
    def __init__(self, prefix=None, **kwargs):
        super().__init__(**kwargs)
        if prefix is not None and not isinstance(prefix, str):
            raise TypeError("Argument 'prefix' is expected to be a str, but is {}".format(type(prefix)))
        self.prefix = prefix

    def _prefix(self, cls):
        return self.prefix or getattr(cls, '__resolver_prefix__', None) or getattr(cls, '__prefix__', None)

    def _resolve_arg(self, name, value, defaults, cls):
        lookup = name.upper()
        prefix = self._prefix(cls)
        if prefix is not None:
            lookup = prefix.upper() + '_' + lookup
        newval = os.environ.get(lookup, Missing)
        if newval is Missing:
            self.logger.info("Cannot resolve argument '{}' of {}. Try to set environment variable '{}'".format(
                name, cls, lookup))
        return newval
