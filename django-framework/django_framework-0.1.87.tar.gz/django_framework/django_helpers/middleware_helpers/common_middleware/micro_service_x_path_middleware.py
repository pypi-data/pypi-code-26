from django.conf import settings
from django_framework.django_helpers.middleware_helpers.base_middleware import BaseMiddleware

try:
    SERVER_NAME = settings.SERVER_NAME
    
except Exception as e:
    print('-------------------------------------------------------------------')
    SERVER_NAME = 'default'
    print('Trying to use the micro_service_x_path_middleware but cannot find settings.SERVER_NAME')
    print('Error', e)
    print('Set to default')
    print('-------------------------------------------------------------------')


class MicroServiceXPathMiddleware(BaseMiddleware):
    '''Adds a field: X-Path to all headers so that it is possible to trace the specific route
    of each path. It becomes easier to debug this way.
    '''
    def _pre_action(self, request):
        pass
    
    def _post_action(self, request, response):
        
        if response.get('X-PATH') == None:
            response['X-PATH'] = ''

        try:
            response['X-PATH']+= '|{name}'.format(name = SERVER_NAME)
        except:
            pass
        return response
