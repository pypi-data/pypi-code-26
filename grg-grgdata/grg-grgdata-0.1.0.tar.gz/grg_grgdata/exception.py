'''a collection of all grg_grgdata exception classes'''


class GRGDataException(Exception):
    '''root class for all GRGData Exceptions'''
    pass


class GRGDataValidationError(GRGDataException):
    '''for errors that occur while attempting to validate the correctness of
        a parsed GRG data file
    '''
    pass


class GRGDataWarning(Warning):
    '''root class for all GRG data warnings'''
    pass
