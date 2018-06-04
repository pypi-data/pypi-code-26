class CaughtException(Exception):
    def __init__(self, message, caught_exception):
        super(CaughtException, self).__init__(message)
        self.__cause__ = caught_exception
