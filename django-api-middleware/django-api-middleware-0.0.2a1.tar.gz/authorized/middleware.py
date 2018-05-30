"""
==============
API Middleware
==============

"""
from django.http import JsonResponse
from django.conf import settings
from ua_parser import user_agent_parser
from authorized import api_check
from authorized import api_token
from authorized import api_utils
class APIAuthRequestMiddleware:
    """
    Middleware that will evaluate if the incoming request is
    authorized to comunicate with the current application.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.custom_response = None
        self.key = None

    def __call__(self, request):
        # when in debug mode, the middleware will skip incoming requests that come from sources like browsers or Postman.
        if settings.DEBUG:
            parsed_agent = user_agent_parser.Parse(request.META['HTTP_USER_AGENT'])
            if 'Postman' or 'Mozilla' or 'Chrome' or 'insomnia' in parsed_agent['string']:
                response = self.get_response(request)
                response['Application-Token'] = api_token.generate()
                return response
        # will skip a path if placed on the settings variable
        if self.skip_path(request.path):
            response = self.get_response(request)
            response['Application-Token'] = api_token.generate()
            return response
        # if there is no key, the app will return a 'service not available status', either APP_KEY or APP_NAME is missing
        if not api_utils.has_key() and not api_utils.has_name():
            response = JsonResponse({'message': 'Application has not being set properly.'}, status=503)
            response['Application-Token'] = api_token.generate()
            return response

        # process header token
        if self.process_header(request.META):
            response = self.get_response(request)
        else:
            response = self.custom_response

        # Before returning response headers can be appended to the response object, below this comment is an appropiate place.
        response['Application-Token'] = api_token.generate()
        return response

    def skip_path(self, request_path):
        """
        Will handle all the paths that are in the settings variable.
        """
        # Exclude paths in the settings variable list. no headers will be added in the response.
        if settings.IGNORED_PATHS:
            # to allow any path the the only item required in the list is '*'
            if settings.IGNORED_PATHS[0] == '*':
                return True
            # otherwise the list will be iterated and paths in the list will processed
            for path in settings.IGNORED_PATHS:
                if str(request_path).replace('/', '').startswith(path):
                    return True
        return False

    def process_header(self, request_headers):
        """
        Process 'Application-Token' header provided in the request, search the application name in the database table and will create the response accordingly.
        """
        token = api_check.header_token(request_headers)
        if token['has_token']:
            token_verified = api_token.verify(token['token'])
            if token_verified['is_valid']:
                app = api_check.is_application_authorized(token_verified['app_name'])
                if app['is_authorized']:
                    return True
                else:
                    self.custom_response = JsonResponse({'message': app['message']}, status=403)
                    return False
            else:
                self.custom_response = JsonResponse({'message': token_verified['message']}, status=500)
                return False
        else:
            self.custom_response = JsonResponse({'message': token['message']}, status=403)
            return False
