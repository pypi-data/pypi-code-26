# Copyright 2018 Smithsonian Astrophysical Observatory
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
# disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
Data model concepts, i.e. types and roles, are represented by portable strings that are globally
unique. Such identifiers can be used in different serialization formats to map data and metadata
to the data model elements they represent.

VO-DML types are mapped to Python classes.

This module contains a :py:class:`~TypeRegistry` class that can be used to map VO-DML
type identifiers to the corresponding Python class. This class is a singleton, which ensures that
types are registered for the entire process life cycle.

The module also defines a :py:class:`~VO` class decorator that can be used to map
Python classes to the VO-DML type they represent. When classes with the decorator are imported
they are registered by the ID passed to the decorator.

Example::

    >>> from rama.utils.registry import VO, TypeRegistry
    >>> @VO('foo:bar')
    ... class MyClass:
    ...   pass
    ...
    >>> TypeRegistry.instance.get_by_id('foo:bar')
    <class '....MyClass'>

Note that trying to instantiate the registry results in an exception:

    >>> from rama.utils.registry import TypeRegistry
    >>> TypeRegistry()
    Traceback (most recent call last):
      ...
    TypeError: Singletons must be accessed through `instance`.


"""

import inspect

from rama.utils import Singleton


@Singleton
class TypeRegistry:
    """
    A registry for VO-DML types
    """
    instance = None

    def __init__(self):
        self._type_map = {}

    # TODO docstrings
    def get_by_id(self, vodml_id):
        element_class = self._type_map.get(vodml_id, None)
        if element_class is None:
            raise ValueError(f"Cannot find element with type id: {vodml_id}")
        return element_class

    def add(self, cls):
        if hasattr(cls, 'vodml_id') and inspect.isclass(cls):
            self._type_map[cls.vodml_id] = cls

    def clean(self):
        self._type_map = {}


class VO:
    """
    A class decorator to register Python classes
    """
    def __init__(self, vodml_id):
        self.vodml_id = vodml_id

    def __call__(self, cls):
        cls.vodml_id = self.vodml_id
        TypeRegistry.instance.add(cls)
        return cls
