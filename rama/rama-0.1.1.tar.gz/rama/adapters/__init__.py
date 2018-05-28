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
This package provides adapters for common data model classes related to coordinates and
measurements. Note that at the time of this writing the VOTable parser is already astropy-aware, and it returns
astropy quantities and columns whenever possible.

The adapters in this module take it to the next level and provide a seamless bridge from standard model objects to
astropy objects. The adapters are applied on the fly when parsing a standard object, if the standard model class
is decorated with the :py:class:`~rama.utils.Adapter` decorator, which accepts the adapter class as an argument.

For example::

    >>> from rama.utils import Adapter
    >>> from rama.utils.registry import VO
    >>> from rama.framework import Attribute, BaseType
    >>> class MyAdapter:
    ...     def __init__(self, standard_obj):
    ...         self.ultimate = standard_obj.standard_attribute
    >>> @VO("some:id")
    ... @Adapter(MyAdapter)
    ... class MyStandard(BaseType):
    ...     standard_attribute = Attribute('foo:bar')

Every time the parser will build an instance of the ``Standard`` class, it will pass it to the `Adapter` class::

    >>> from io import StringIO
    >>> xml = StringIO('''<INSTANCE dmtype="some:id">
    ... <ATTRIBUTE dmrole="foo:bar">
    ...   <LITERAL dmtype="ivoa:integer" value="42"/>
    ... </ATTRIBUTE>
    ... </INSTANCE>
    ... ''')
    >>> from rama import read
    >>> parsed = read(xml).find_instances(MyStandard)[0]
    >>> print(type(parsed))
    <class '....MyAdapter'>
    >>> print(parsed.ultimate)
    42

There are no restrictions on how the adapter needs to be implemented. In the above example it simply implement a
regular Python initializer method to initialize itself with data from the standard object. In other cases
adapters might implement the ``__new__`` method and return a completely different object.

"""
