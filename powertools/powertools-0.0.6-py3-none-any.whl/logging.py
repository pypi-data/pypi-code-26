# powertools.logging

'''
logging recipes
'''

#-------------------------------------------------------------------------------------------------#

import sys
import logging

handler = logging.StreamHandler( stream=sys.stdout )
formatter = logging.Formatter( )
handler.setFormatter( formatter )

logging.basicConfig(handlers=(handler,))
#logging.getLogger( ).handlers[0].setFormatter( formatter )

#-------------------------------------------------------------------------------------------------#

from .export import export

from inspect import currentframe
from inspect import getouterframes
from functools import partialmethod

import coloredlogs
coloredlogs.install(level='INFO')

from . import term

#-------------------------------------------------------------------------------------------------#

levels = dict(
    FATAL   =50,
    ERROR   =40,
    WARNING =30,
    INFO    =20,
    DEBUG   =10,
)

loggers = lambda: map( logging.getLogger, logging.Logger.manager.loggerDict )


#-------------------------------------------------------------------------------------------------#

@export
class AutoLogger :
    ''' automatically set the name of the logger to the instance's module.
        format the log message indentation according to caller stack depth
        add the caller's name to the log message
        provide a context manager to temporarily display debug messages
        ``` log = AutoLogger()
            with log.setdebug:
                log.debug('hello', ' world')
        ```
    '''
    def __init__( self ) :
        self.name        = getouterframes( currentframe( ) )[1].frame.f_globals['__name__']
        self._base_depth = len( getouterframes( currentframe( ) ) )
        self.logger      = logging.getLogger( self.name )
        self.logger.setLevel( logging.INFO )

        self.rootlogger:logging.Logger = logging.getLogger()

        coloredlogs.install(logger=self.logger, fmt='%(message)s', level=logging.DEBUG)

    #################
    def _print( self, loglevel, *args, stackpop=0, add_indent=False, clean=False, **kwargs) :
        # print('self', self)
        stackdepth  = len(getouterframes( currentframe())) - stackpop - self._base_depth
        frameinfo   = getouterframes( currentframe( ) )[1 + stackpop]
        frame       = frameinfo.frame
        funcname    = frameinfo.function
        try:
            methodclass = frame.f_locals['self'].__class__
        except KeyError as e:
            methodclass = None
        qualname        = (methodclass.__name__+'.' if methodclass is not None else '') + funcname

        self.logger.log(
            levels[loglevel],
            ''.join( str( a ) for a in [
                *((
                    loglevel, ':', ' ' * (7 - len( loglevel )),
                    term.red( stackdepth * '--->' if add_indent else '' ),
                    term.white(self.name,'.'), term.dcyan(qualname), term.white( ":: "),
                  ) if not clean else ()),

                *args
            ]),
        **kwargs)

    #################
    critical    = partialmethod( _print, 'FATAL')
    error       = partialmethod( _print, 'ERROR' )
    warn        = partialmethod( _print, 'WARNING' )

    print       = partialmethod( _print, 'INFO', clean=True)
    info        = partialmethod( _print, 'INFO' )
    dinfo       = partialmethod( _print, 'INFO', add_indent=True )
    debug       = partialmethod( _print, 'DEBUG', add_indent=True )
    dprint      = partialmethod( _print, 'DEBUG', clean=True )

    #################
    @staticmethod
    def setWarning():
        for logger in loggers() :
            logger.setLevel( logging.WARNING )

    @staticmethod
    def setDebug():
        for logger in loggers() :
            logger.setLevel( logging.DEBUG )

    @staticmethod
    def setInfo() :
        for logger in loggers() :
            logger.setLevel( logging.INFO )

    #################
    def remove_all(self):
        for handler in self.rootlogger.handlers:
            self.rootlogger.removeHandler(handler)

    def add_stdout(self):
        self.rootlogger.addHandler(logging.StreamHandler(sys.stdout))

    def add_file(self):
        ''' Not Implemented
        '''
        self.rootlogger.addHandler(...)

    #################
    class _setdebug:
        ''' temporarily enable debug messages for all loggers during scope
        '''
        def __init__(self, logger):
            self.logger = logger

        def __enter__(self):
            for logger in loggers():
                logger.setLevel( logging.DEBUG )


        def __exit__(self, exc_type, exc_value, traceback ):
            for logger in loggers():
                logger.setLevel( logging.INFO)

    @property
    def setdebug( self ) :
        ''' temporarily enable debug messages for all loggers during context
            context manager object created and returned as a property
        '''
        return self._setdebug(self.logger)

#####

# [0]: https://stackoverflow.com/questions/17065086/how-to-get-the-caller-class-name-inside-a-function-of-another-class-in-python

#-------------------------------------------------------------------------------------------------#
