"""
====================
API Utilities Module
====================
"""
import os
from django.conf import settings

def has_key():
    """
    Verifies if app has an APP_KEY, either in the project settings or in system environment.
    """
    if os.getenv('APP_KEY') is not None:
        return True
    try:
        if settings.APP_KEY is not None:
            return True
    except AttributeError:
        return False

def has_name():
    """
    Verifies if app has an APP_NAME settings variable.
    """
    try:
        settings.APP_NAME
    except AttributeError:
        return False
    else:
        return True

def get_key():
    """
    Returns the app key
    
    :return: app_key for encoding and decoding jwt tokens.
    """
    app_key = None
    try:
        if os.getenv('APP_KEY') is not None:
            app_key = os.getenv('APP_KEY')
        elif settings.APP_KEY is not None:
            app_key = settings.APP_KEY
    except AttributeError:
        app_key = None
    return app_key

def get_name():
    """
    Returns the application Name
    
    :return: application name to be appended in the token payload.
    """
    app_name = None
    try:
        app_name = settings.APP_NAME
    except AttributeError:
        return None
    else:
        return app_name
