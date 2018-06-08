# $BEGIN_SHADY_LICENSE$
# 
# This file is part of the Shady project, a Python framework for
# real-time manipulation of psychophysical stimuli for vision science.
# 
# Copyright (C) 2017-18  Jeremy Hill, Scott Mooney
# 
# Shady is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/ .
# 
# $END_SHADY_LICENSE$
"""
Aside from a couple of internal routines for automatic doc generation,
this module is designed to contain enpty classes whose names and
docstrings explain some of the broader concepts of Shady.

Examples of use - from IPython, using `?` syntax::

	In [1]: import Shady
	
	In [2]: Shady.Documentation.ManagedProperties?
	                            ^ tab-completion is your friend here

Or from a vanilla Python prompt:

	>>> import Shady
	>>> help( Shady.Documentation.ManagedProperties )

"""

__all__ = [
	# will be filled automatically...
]

import os      as _os
import re      as _re
import glob    as _glob
import inspect as _inspect

try: __file__
except NameError:
	try: frame = _inspect.currentframe(); __file__ = _inspect.getfile( frame )
	finally: del frame  # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
_HERE = _os.path.dirname( _os.path.realpath( __file__ ) )
_DOCDIR = _os.path.realpath( _os.path.join( _HERE, '..', '..', 'doc' ) )
_AUTODIR = _os.path.join( _DOCDIR, 'auto' )
_SPHINXDOC = any( _os.environ.get( varName, '' ).lower() not in [ '', '0', 'false' ] for varName in [ 'SPHINX' ] )
_MATCH_RST = [
	[ 'crossref',    _re.compile(        r':doc:`(.*?)\s*(<[a-z0-9_\-\+]+>)?`(_+)?', _re.I ),  lambda m: _os.path.basename( m.groups()[ 0 ] ) ],
	[ 'role',        _re.compile( r':[a-z0-9_]+:`(.*?)\s*(<[a-z0-9_\-\+]+>)?`(_+)?', _re.I ),  r'\1' ],
	[ 'comment',     _re.compile( r'\n[\t ]*\.\.[\t ]*[a-z0-9_]+(:+.*)?(\n[\t ]*(?=\n))?', _re.I ), '' ],
	[ 'examples_*',  _re.compile( r'^(\s+)examples_([a-zA-Z0-9_\-\+]+)\s*$', _re.MULTILINE ), r'\1examples/\2.py' ],
	[ 'doublecolon', _re.compile( r':(?=:[\t ]*\n)' ), '' ],
	[ 'hyperlink',   _re.compile(             r'`(.*?)\s*(<[^<>]+?>)?`_+',    _re.I ),  lambda m: m.groups()[ 0 ] ],
]
_MATCH_TITLE = _re.compile( r'\s*([\S ]+)[\t ]*\n[\-\^\=\~]{3,}[\t ]*\n' )
_RST = {}

	
class _DynamicDocString( object ):
	def __set__( self, instance, value ): instance.__class__._doc = value
	def __get__( self, instance, owner=None ):
		doc = owner._doc
		if not _SPHINXDOC:
			for name, match, replace in _MATCH_RST:
				doc = _re.sub( match, replace, doc )
		return doc.lstrip( '\n' ).rstrip()
#class _DocumentationOnly( object ): __slots__ = []
_DocumentationOnly = object

def _extract( rst, keyword ):
	m = _re.search( r'\n[\t ]*\.\.[\t ]*' + keyword + '(:+\s*(.+?))\s*\n', rst, _re.I | _re.MULTILINE )
	if m: return m.group( 2 )

def _as_filename( x, locations=( '.', 'rst' ) ):
	if '\n' in x: return
	if _os.path.isfile( x ): return _os.path.realpath( x )
	if _os.path.isabs( x ): return
	for location in locations:
		attempt = _os.path.join( _HERE, location, x )
		if _os.path.isfile( attempt ): return _os.path.realpath( attempt )		
	
def _doc( doc ):
	source_filename = _as_filename( doc )
	if source_filename: doc = open( source_filename, 'rt' ).read().replace( '\r\n', '\n' ).replace( '\r', '\n' )
	doc = '\n' + doc.lstrip( '\n' ).rstrip() + '\n'
	doc = doc.replace( '\t', ' ' * 4 )
	names = filename = None
	#names = _extract( doc, 'objectname' )
	#filename = _extract( doc, 'filename' )
	if source_filename:
		stem = _os.path.splitext( _os.path.basename( source_filename ) )[ 0 ]
		if not names: names = stem
		if not filename: filename = stem
	if not names:
		match = _re.match( _MATCH_TITLE, doc )
		if match: names = match.groups()[ 0 ].strip().replace( '-', ' ' ).title().replace( ' ', '' )
		elif source_filename: names = _os.path.splitext( _os.path.basename( source_filename ) )[ 0 ]
		else: names = None
	if not names: raise ValueError( 'failed to infer name of doc object %r' % ( source_filename if source_filename else doc[ :50 ] ) )
	if isinstance( names, str ): names = names.replace( ',', ' ' ).split()
	names = list( names )
	doc = '\n.. top:\n' + doc
	class wrapper:   # (_DocumentationOnly):
		__doc__ = _DynamicDocString()
		__slots__ = []
		_doc, _names, _filename, _source_filename  = doc, names, filename, source_filename
	if names: wrapper.__name__ = names[ 0 ]
	for name in names:
		globals()[ name ] = wrapper
		break # comment this out to assign all names to this module's namespace; retain it to assign only the canonical names...
	if names: __all__.append( names[ 0 ] ) # ...but either way, export canonical names only
	return wrapper

def _auto_compose_rst():
	# first, the example scripts (updating the ExampleScripts index doc as we go)
	packageLocation = _HERE.replace( '\\', '/' ).rstrip( '/' ) + '/'
	examples = sorted( _glob.glob( packageLocation + 'examples/*.py' ) )
	for i, fullFilePath in enumerate( examples ):
		shortFilePath = fullFilePath.replace( '\\', '/' )[ len( packageLocation ): ]
		literalIncludePath = _os.path.relpath( fullFilePath, _AUTODIR )
		stem, xtn = _os.path.splitext( _os.path.basename( shortFilePath ) )
		rstStem = 'examples_' + stem
		if stem == 'showcase':
			ExampleScripts._doc = ExampleScripts._doc.format( **locals() ) # fills in {stem} and {shortFilePath} for first example
		ExampleScripts._doc += '   %s\n' % rstStem
		title = shortFilePath
		underline = '=' * len( title )
		_RST[ rstStem ] = """\
{title}
{underline}

This is one of the :doc:`example scripts <ExampleScripts>` included
with Shady. These scripts can be run conventionally like any
normal Python script, or you can choose to run them as
interactive tutorials, for example with `python -m Shady demo {stem}`

.. literalinclude:: {literalIncludePath}

""".format( **locals() )

	# And now everything else:
	for name in __all__:
		obj = globals()[ name ]
		try: ( obj._filename, obj._names, obj._doc )
		except: continue
		filename = obj._filename
		if not filename and obj._names: filename = obj._names[ 0 ]
		if not filename: continue
		_RST[ filename ] = obj._doc

def _generate_rst_files( dummy=False ):
	if not _os.path.isdir( _DOCDIR ): print( 'Directory not found: ' + _DOCDIR ); return
	if not _os.path.isdir( _AUTODIR ): _os.makedirs( _AUTODIR )
	oldFiles = sorted( _glob.glob( _os.path.join( _AUTODIR, '*.rst' ) ) )
	for oldFile in oldFiles:
		print( 'removing ' + oldFile )
		if not dummy: _os.remove( oldFile )
	for fileStem, content in sorted( _RST.items() ):
		fileName = fileStem + '.rst'
		filePath = _os.path.join( _AUTODIR, fileName )
		print( 'writing ' + filePath )
		if dummy: continue
		with open( filePath, 'wt' ) as fh: fh.write( content + '\n' )

################################################################################
################################################################################

for _filename in sorted( _glob.glob( _os.path.join( _HERE, 'rst', '*.rst' ) ) ): _doc( _filename )

if _SPHINXDOC: _doc( """
Topics
======

.. toctree::

""" + ''.join( '   %s\n' % name for name in __all__ if name not in 'Overview License'.split() ) )

_doc( """

Example Scripts
===============

The following example scripts are included as part of the Shady package.
They can be run conventionally like any normal Python script.
Alternatively, you can explore them interactively piece-by-piece with
(for example)::

    python -m Shady demo {stem}

From inside Python, this is equivalent to:

.. code:: python

    from Shady import RunShadyScript, PackagePath
    RunShadyScript( PackagePath( '{shortFilePath}' ) )

List of examples
----------------

.. toctree::
      
""" )
################################################################################
################################################################################

_auto_compose_rst()
from .Rendering import Screens, World, Stimulus
