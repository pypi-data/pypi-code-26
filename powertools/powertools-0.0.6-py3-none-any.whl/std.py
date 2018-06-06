#-- powertools.std

"""
better get tested
"""


#----------------------------------------------------------------------------------------------#

##############################
def name( obj ) -> str :
    ''' easier access to object name '''
    return str( obj.__name__ )

##############################
def qualname( obj: object ) -> str :
    ''' module and qualified object name '''
    return f'{obj.__module__}.{obj.__qualname__}'


#----------------------------------------------------------------------------------------------#
