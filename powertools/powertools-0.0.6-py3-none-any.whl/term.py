
'''
terminal colors
'''

from termcolor import colored
from functools import partial
from contextlib import suppress

#----------------------------------------------------------------------------------------------#

cprint = lambda color, *args, bold=True,: (
    colored(
        ''.join(str(a) for a in args),
        color, attrs=['bold'] if bold else []
    )
)


###################################################
white   = partial( cprint, 'white',     bold=True )
red     = partial( cprint, 'red',       bold=True )
green   = partial( cprint, 'green',     bold=True )
blue    = partial( cprint, 'blue',      bold=True )
pink    = partial( cprint, 'magenta',   bold=True )
yellow  = partial( cprint, 'yellow',    bold=True )
cyan    = partial( cprint, 'cyan',      bold=True )

dwhite  = partial( cprint, 'white',     bold=False )
dred    = partial( cprint, 'red',       bold=False )
dgreen  = partial( cprint, 'green',     bold=False )
dblue   = partial( cprint, 'blue',      bold=False )
dpink   = partial( cprint, 'magenta',   bold=False )
dyellow = partial( cprint, 'yellow',    bold=False )
dcyan   = partial( cprint, 'cyan',      bold=False )


#----------------------------------------------------------------------------------------------#

def init_color():
    ''' encapsulate terminal color configuration so it could be more easily turned off if necessary
        only call this inside functions to prevent configuration bleed during module import
    '''
    ### enable color on windows
    with suppress(ImportError):
        import colorama
        colorama.init()

    ###
    import colored_traceback
    colored_traceback.add_hook( style='dark' )


#----------------------------------------------------------------------------------------------#

def c( input_string:str ) -> str:
    ''' convert custom colorization syntax to ansi color terminal codes '''
    result = input_string
    raise NotImplementedError
    return result


#----------------------------------------------------------------------------------------------#
