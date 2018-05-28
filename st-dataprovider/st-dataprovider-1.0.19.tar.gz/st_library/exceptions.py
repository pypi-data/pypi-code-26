import json


class LibraryException(Exception):
    """
    Base exception class for the Library.

    """


class ServiceRequestError(LibraryException):
    """
    This exception is raised when request to the Service failed.

    """

    def __init__(self, status, content):
        self.status = status
        self.content = content
        self.message = u'HTTP request failed. Status code : {} '.format(status)
        # Try extract a message from the body; swallow possible resulting ValueErrors and KeyErrors.
        try:
            error = json.loads(content)['error']
            if 'errors' in error:
                error = error['errors'][0]
            self.message += u': ' + error['message']
        except Exception:
            if content:
                lines = content.split(u'\n')
                if lines:
                    self.message += u': ' + lines[0]

    def __str__(self):
        return self.message


class InternalError(LibraryException):
    """
    An internal logic error.

    """


class PerformanceRequired(LibraryException):
    """
    This exception is raised when Performance is mandatory for executing operation,
    but it is not defined for current Environment.

    """


class SchemaCreationError(LibraryException):
    """
    An error of schema creation

    """


class DatabaseConnectionError(LibraryException):
    """
    An error of connection to database

    """


class DatabaseNotFound(LibraryException):
    """
    An error raising after try to access the missing database
    """
