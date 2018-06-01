"""Defines errors thrown by lib-freshservice."""
import logging


class FreshserviceError(Exception):

    """An error occurred in the Freshservice module."""


class BadInput(FreshserviceError):

    """The user passed something, that doesn't match the model."""


class AuthenticationFailed(FreshserviceError):

    """Invalid or missing API key."""


class UnexpectedValue(FreshserviceError):

    """The API passed a value, that this wrapper doesn't understand."""


class UserSearchFailed(FreshserviceError):

    """Couldn't find user with given email"""


class AgentSearchFailed(FreshserviceError):

    """Couldn't find agent with given email"""


class ResponseError(FreshserviceError):

    """Response is not JSON or contains errors."""

    def __init__(self, request, response):
        super().__init__()
        self.request = request
        self.response = response

        logging.error('-----------Request-----------\n' + str(request.body))
        if response:
            logging.error('-----------Response-----------\n' + str(response))
        else:
            logging.error('The Freshservice response is not in JSON format')

    def __str__(self):
        return self.request.method + ' ' + self.request.url
