from django.contrib import admin
from gcb_web_auth.models import *

# Register your models here.
admin.site.register(OAuthService)
admin.site.register(OAuthToken)
admin.site.register(DukeDSAPIToken)
admin.site.register(GroupManagerConnection)
admin.site.register(DDSUserCredential)
admin.site.register(DDSEndpoint)
