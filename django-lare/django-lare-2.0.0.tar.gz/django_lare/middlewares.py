from django_lare.models import Lare


class LareMiddleware(object):
    def process_request(self, request):
        request.lare = Lare(request)

    def process_response(self, request, response):
        if request.lare.is_enabled():
            response['X-LARE-VERSION'] = request.lare.version
        return response

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request=None):
        self.process_request(request)
        response = self.get_response(request)
        self.process_response(request, response)
        return response
