from django.http import HttpResponseRedirect
from django.conf import settings

class LoginRequiredMiddleware:
	def process_request(self, request):
		if not request.user.is_authenticated():
			return HttpResponseRedirect(settings.LOGIN_URL)
