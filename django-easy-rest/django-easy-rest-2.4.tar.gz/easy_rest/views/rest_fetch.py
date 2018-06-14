from django.views.generic import TemplateView
from django.http import HttpResponse
import json


class TemplateContextFetcherView(TemplateView):
    def post_method_override(self, *args, **kwargs):
        return HttpResponse("To override the post method declare post_method_override in your view - django-easy-rest")

    def post(self, request, *args, **kwargs):
        """

        :param request: WSGI request
        :param args:
        :param kwargs:
        :return: HttpResponse containing updated context
        """

        action = request.POST.get("action", "")
        if action == "fetch-content":
            return HttpResponse(json.dumps(self.get_context_data(request=request)))

        return self.post_method_override(request, *args, **kwargs)
