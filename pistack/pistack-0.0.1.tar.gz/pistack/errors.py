class CommsError(Exception):
    pass

class InvalidCommandError(CommsError):
    pass

class CrcFailureError(CommsError):
    pass

class NoResponseError(CommsError):
    pass

class ResponseLengthWrongError(CommsError):
    pass

class InvalidResponseAddressError(CommsError):
    pass

class InvalidPrefixError(CommsError):
    pass

class InvalidPiError(CommsError):
    pass

class InvalidErrorCode(Exception):
    pass
