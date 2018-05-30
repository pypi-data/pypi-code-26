"""
==========================
Authorization Check Module
==========================
"""
from django.core.exceptions import ObjectDoesNotExist
from authorized.models import Applications

def is_application_authorized(app_name):
    """
    Verifies if the application passed is authorized to make requests to the current application.

    :param app_name: name of the application to be evaluated.
    :return: dictionary containig a message and an authorized status.
    """
    response = {}
    response['is_authorized'] = False
    try:
        # try to get the application passed
        app = Applications.objects.get(name=app_name)
    except ObjectDoesNotExist:
        # if application does not exists, it has not been registered yet.
        response['message'] = 'Unauthorized request.'
    else:
        # if application is found check wether it has permissions or not.
        if app.can_request:
            response['is_authorized'] = True
            response['messsage'] = ''
        else:
            response['message'] = 'Unauthorized request.'

    return response

def is_response_trusted(app_name):
    """Verifies if the response is coming from a trusted source.

    :param app_name: name of the application to be evaluated

    :return: dictionary, containing a message and an authorized status.
    """
    response = {}
    response['is_authorized'] = False
    if Applications.objects.filter(name=app_name).exists():
        response['is_authorized'] = True
    return response

def header_token(request_headers):
    """
    Checks wether the headers dictionary contains the required header to be processed
    :param request_headers: a dictionary containing the request headers.
    :return: a dictionary containing the token existence status and the token itself
    """
    response = {}
    response['has_token'] = False
    try:
        app_token = request_headers['HTTP_APPLICATION_TOKEN']
    except KeyError:
        response['message'] = 'Invalid request'
    else:
        response['has_token'] = True
        response['token'] = app_token
    return response

def response_header_token(api_request_response):
    """Checks whether the response is from a trusted source.

    :param response: response from api_request
    :type response: Response

    :return: True if the response is from a trusted source.
    :rtype: bool
    """
    response = {}
    response['has_token'] = False
    if api_request_response.headers.get('Application-Token') is not None:
        response['has_token'] = True
        response['token'] = api_request_response.headers.get('Application-Token')
    return response
