import argparse
import json
import importlib
import importlib.abc
import importlib.machinery
import inspect
import logging
import pkg_resources
import sys
import typing
from xmlrpc import client as xmlrpc  # type: ignore

from d3m import exceptions, namespace
from d3m.primitive_interfaces import base

__all__ = ('search', 'get_primitive', 'get_primitive_by_id', 'get_loaded_primitives', 'load_all', 'register_primitive', 'discover')

logger = logging.getLogger(__name__)


class _SENTINEL_TYPE:
    __slots__ = ()

    def __repr__(self) -> str:
        return '_SENTINEL'


_SENTINEL = _SENTINEL_TYPE()

_loaded_primitives: typing.Set[typing.Type[base.PrimitiveBase]] = set()


def search(*, primitive_path_prefix: str = None) -> typing.Sequence[str]:
    """
    Returns a list of primitive paths (Python paths under ``d3m.primitives`` namespace)
    for all known (discoverable through entry points) primitives, or limited by the
    ``primitive_path_prefix`` search argument.

    Not all returned primitive paths are not necessary loadable and it is not necessary that
    they are all really pointing to primitive classes, because this method does not try to
    load them yet to determine any of that.

    Parameters
    ----------
    primitive_path_prefix : str
        Optionally limit returned primitive paths only to those whose path start with ``primitive_name_prefix``.

    Returns
    -------
    Sequence[str]
        A list of primitive paths.
    """

    if primitive_path_prefix is None:
        primitive_path_prefix = ''

    results = []

    for entry_point in pkg_resources.iter_entry_points('d3m.primitives'):
        primitive_path = 'd3m.primitives.{entry_point_name}'.format(
            entry_point_name=entry_point.name,
        )

        if primitive_path.startswith(primitive_path_prefix):
            results.append(primitive_path)

    return results


def get_primitive(primitive_path: str) -> typing.Type[base.PrimitiveBase]:
    """
    Loads (if not already) a primitive class and returns it.

    Parameters
    ----------
    primitive_path : str
        A Python path under ``d3m.primitives`` namespace of a primitive.

    Returns
    -------
    Type[PrimitiveBase]
        A primitive class.
    """

    if not primitive_path:
        raise exceptions.InvalidArgumentValueError("Primitive path is required.")

    if not primitive_path.startswith('d3m.primitives.'):
        raise exceptions.InvalidArgumentValueError("Primitive path does not start with \"d3m.primitives\".")

    path, name = primitive_path.rsplit('.', 1)

    module = importlib.import_module(path)

    return getattr(module, name)


def get_primitive_by_id(primitive_id: str) -> typing.Type[base.PrimitiveBase]:
    """
    Returns a primitive class based on its ID from all currently loaded primitives.

    Parameters
    ----------
    primitive_id : str
        An ID of a primitive.

    Returns
    -------
    Type[PrimitiveBase]
        A primitive class.
    """

    for primitive in get_loaded_primitives():
        if primitive.metadata.query()['id'] == primitive_id:
            return primitive

    raise exceptions.InvalidArgumentValueError("Unable to get primitive '{primitive_id}'.".format(primitive_id=primitive_id))


def get_loaded_primitives() -> typing.Sequence[typing.Type[base.PrimitiveBase]]:
    """
    Returns a list of all currently loaded primitives.

    Returns
    -------
    Sequence[Type[PrimitiveBase]]
        A list of all currently loaded primitives.
    """

    return list(_loaded_primitives)


def load_all(blacklist: typing.Collection[str] = None) -> None:
    """
    Loads all primitives available and populates ``d3m.primitives`` namespace with them.

    If a primitive cannot be loaded, an error is logged, but loading of other primitives
    continue.

    Parameters
    ----------
    blacklist : Collection[str]
        A collection of primitive path prefixes to not (try to) load.
    """

    if blacklist is None:
        blacklist = []

    for primitive_path in search():
        if any(primitive_path.startswith(blacklist_prefix) for blacklist_prefix in blacklist):
            continue

        try:
            get_primitive(primitive_path)
        except Exception:
            logger.exception("Could not load the primitive: %(primitive_path)s", {'primitive_path': primitive_path})


def register_primitive(primitive_path: str, primitive: typing.Type[base.PrimitiveBase]) -> None:
    """
    Registers a primitive under ``d3m.primitives`` namespace.

    This is useful to register primitives not necessary installed on the system
    or which are generated at runtime. It is also useful for testing purposes.

    ``primitive_path`` has to start with ``d3m.primitives``.

    Parameters
    ----------
    primitive_path : str
        A primitive path to register a primitive under.
    primitive : Type[PrimitiveBase]
        A primitive class to register.
    """

    if not primitive_path:
        raise exceptions.InvalidArgumentValueError("Path under which to register a primitive is required.")

    if not primitive_path.startswith('d3m.primitives.'):
        raise exceptions.InvalidArgumentValueError("Path under which to register a primitive does not start with \"d3m.primitives\".")

    if not inspect.isclass(primitive):
        raise exceptions.InvalidArgumentTypeError("Primitive to register has to be a class.")

    if not issubclass(primitive, base.PrimitiveBase):
        raise exceptions.InvalidArgumentTypeError("Primitive to register is not a subclass of PrimitiveBase.")

    modules_path, name = primitive_path.rsplit('.', 1)
    # We remove "d3m.primitives" from the list of modules.
    modules = modules_path.split('.')[2:]

    if 'd3m.primitives' not in sys.modules:
        import d3m.primitives  # type: ignore

    # Create any modules which do not yet exist.
    current_path = 'd3m.primitives'
    for module_name in modules:
        module_path = current_path + '.' + module_name

        if module_path not in sys.modules:
            try:
                importlib.import_module(module_path)
            except ModuleNotFoundError:
                # This can happen if this module is not listed in any of entry points. But we want to allow
                # registering primitives also outside of existing entry points, so we create a module here.

                # Because we just could not load the module, we know that if the attribute exists,
                # it has to be something else, which we do not want to clobber.
                if hasattr(sys.modules[current_path], module_name):
                    raise ValueError("'{module_path}' is already defined.".format(module_path))

                module_spec = importlib.machinery.ModuleSpec(module_path, namespace.Loader(), is_package=True)
                module = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(module)

                sys.modules[module_path] = module
                setattr(sys.modules[current_path], module_name, module)

        current_path = module_path

    if hasattr(sys.modules[current_path], name):
        existing_value = getattr(sys.modules[current_path], name)
        # Registering twice the same primitive is a noop.
        if existing_value is primitive:
            return

        # Maybe we are just registering this primitive. But if not...
        if existing_value is not _SENTINEL:
            raise ValueError("'{module}.{name}' is already defined as '{existing_value}'.".format(module=current_path, name=name, existing_value=existing_value))

    setattr(sys.modules[current_path], name, primitive)
    _loaded_primitives.add(primitive)


def discover(index: str = 'https://pypi.org/pypi') -> typing.Tuple[str, ...]:
    """
    Returns package names from PyPi which provide D3M primitives.

    This is determined by them having a ``d3m_primitive`` among package keywords.

    Parameters
    ----------
    index : str
        Base URL of Python Package Index to use.

    Returns
    -------
    Tuple[str]
        A list of package names.
    """

    client = xmlrpc.ServerProxy(index)
    hits = client.search({'keywords': 'd3m_primitive'})
    return tuple(sorted({package['name'] for package in hits}))


def main() -> None:
    logging.basicConfig()

    parser = argparse.ArgumentParser(description="Explore D3M primitives.")
    subparsers = parser.add_subparsers(dest='command', title='commands')
    subparsers.required = True  # type: ignore

    search_parser = subparsers.add_parser(
        'search', help="search locally available primitives",
        description="Searches locally available primitives. Lists registered Python paths to primitive classes for primitives installed on the system.",
    )
    discover_parser = subparsers.add_parser(
        'discover', help="discover primitives available on PyPi",
        description="Discovers primitives available on PyPi. Lists package names containing D3M primitives on PyPi.",
    )
    describe_parser = subparsers.add_parser(
        'describe', help="generate a JSON description of a primitive",
        description="Generates a JSON description of a primitive.",
    )

    search_parser.add_argument(
        '-p', '--prefix', action='store',
        help="primitive path prefix to limit search results to"
    )

    discover_parser.add_argument(
        '-i', '--index', default='https://pypi.org/pypi', action='store',
        help="base URL of Python Package Index to use, default https://pypi.org/pypi"
    )

    describe_parser.add_argument(
        'primitive_path', action='store',
        help="primitive path identifying a primitive to describe"
    )
    describe_parser.add_argument(
        '-i', '--indent', type=int, default=4, action='store',
        help="indent JSON by this much, 0 disables indentation, default 4"
    )
    describe_parser.add_argument(
        '-s', '--sort_keys', default=False, action='store_true',
        help="sort keys in JSON"
    )

    arguments = parser.parse_args()

    if arguments.command == 'search':
        for primitive_path in search(primitive_path_prefix=arguments.prefix):
            print(primitive_path)

    elif arguments.command == 'discover':
        for package_name in discover(index=arguments.index):
            print(package_name)

    elif arguments.command == 'describe':
        primitive = get_primitive(arguments.primitive_path)
        json.dump(primitive.metadata.to_json_structure(), sys.stdout, indent=(arguments.indent or None), sort_keys=arguments.sort_keys)  # type: ignore
        sys.stdout.write('\n')

    else:
        assert False, arguments.command


if __name__ == '__main__':
    main()
