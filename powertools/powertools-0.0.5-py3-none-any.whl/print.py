#-- powertools.out

'''
pretty print functions
'''

from . import term

#-------------------------------------------------------------------------------------------------#

from pprint import PrettyPrinter
_pprinter   = PrettyPrinter()
pprint      = _pprinter.pprint
pformat     = _pprinter.pformat


def add_pprint(cls):
    _pprinter._dispatch[cls.__repr__] = cls.__pprint__


#-------------------------------------------------------------------------------------------------#

from collections import namedtuple

#ToDo: 'tprint' - write to multiple streams

def dictprint( d, pfunc=print ) :
    list( pfunc( f'{str(key):<12}:', value ) for key, value in d.items( ) )

def listprint( l, pfunc=print ) :
    list( pfunc( value ) for value in l )


key_color = term.dwhite
value_color = term.dyellow
def rprint( struct, i=0, quiet=False, pfunc=print ) :

    result = ""
    if isinstance( struct, list ) \
    or isinstance( struct, tuple):  # loop over list/tuple
        for value in struct :
            if isinstance( value, dict  ) \
            or isinstance( value, list  ) \
            or isinstance( value, tuple ) : # recurse on subsequence
                result += rprint( value, i + 2, quiet )

            else :
                line = ' '*i + "- " + value_color(str(value))
                result += line + "\n"
                pfunc( line ) if quiet is False else None

    elif isinstance( struct, dict ) : # loop over dict
        for (key, value) in struct.items( ) :
            line = ' '*i + key_color(f"{str(key)+':':<12} ")
            result += line
            pfunc( line, end='' ) if quiet is False else None

            if isinstance( value, dict  ) \
            or isinstance( value, list  ) \
            or isinstance( value, tuple ) : # recurse on subsequence
                pfunc( "" ) if quiet is False else None
                result += "\n"
                result += rprint( value, i + 2, quiet )

            else :
                cvalue = value_color(str(value))
                result += cvalue + "\n"
                pfunc( cvalue ) if quiet is False else None

    return result


#-------------------------------------------------------------------------------------------------#

