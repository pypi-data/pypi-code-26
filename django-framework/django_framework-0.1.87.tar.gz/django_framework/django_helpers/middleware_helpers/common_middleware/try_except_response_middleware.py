from django.conf import settings
from django_framework.django_helpers.middleware_helpers.base_middleware import BaseMiddleware


try:
    DEBUG_MODE = settings.DEBUG
except Exception as e:
    DEBUG_MODE = False
    print('-----------------------------------------------------------')
    print('django_framework.django_helpers.middleware_helpers.common_middleware.try_except_response_middleware')
    print('Error:', e )
    print('WARNING: settings.DEBUG was not set properly, defaulting to False.')
    print('-----------------------------------------------------------')
    
    
    
try:
    SHOW_DEBUG_TRACEBACK = settings.SHOW_DEBUG_TRACEBACK
except Exception as e:
    SHOW_DEBUG_TRACEBACK = False
    print('-----------------------------------------------------------')
    print('django_framework.django_helpers.middleware_helpers.common_middleware.try_except_response_middleware')
    print('Error:', e )
    print('WARNING: settings.SHOW_DEBUG_TRACEBACK was not set properly, defaulting to False.')
    print('-----------------------------------------------------------')


try:
    SHOW_DEBUG_ERROR = settings.SHOW_DEBUG_ERROR
except Exception as e:
    SHOW_DEBUG_ERROR = False
    print('-----------------------------------------------------------')
    print('django_framework.django_helpers.middleware_helpers.common_middleware.try_except_response_middleware')
    print('Error:', e )
    print('WARNING: settings.SHOW_DEBUG_ERROR was not set properly, defaulting to False.')
    print('-----------------------------------------------------------')



class TryExceptResponseMiddleware(BaseMiddleware):
    '''Adds a field: X-Path to all headers so that it is possible to trace the specific route
    of each path. It becomes easier to debug this way.
    '''
    def _pre_action(self, request):
        pass
    
    def _post_action(self, request, response):
        pass
    
    def process_exception(self, request, exception):
        
        print('AHHHAHAHA')
        