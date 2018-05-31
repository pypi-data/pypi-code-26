from django.conf import settings


from django.core.exceptions import MiddlewareNotUsed


class BaseMiddleware(object):
    DEBUG_ONLY = False
    
    def __init__(self, get_response):
        if self.DEBUG_ONLY == True and settings.DEBUG == True:
            raise MiddlewareNotUsed('This middleware is not used when debug is False')
        
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        
        self._pre_action(request)
        
        response = self.get_response(request)
        
        response = self._post_action(request, response)

        return response
    
    def _pre_action(self, request):
        raise NotImplemented('At the very least please override me with a pass!')
    
    def _post_action(self, request, response):
        raise NotImplemented('At the very least please override me and return response!')