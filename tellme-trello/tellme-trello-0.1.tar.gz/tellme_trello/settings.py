from django.conf import settings, ImproperlyConfigured

def get(setting, default=None):
    key = 'TELLME_%s' % setting
    value = getattr(settings, key, default)
    return value

API_KEY = get('API_KEY')
API_SECRET = get('API_SECRET')
TOKEN = get('TOKEN')
TOKEN_SECRET = get('TOKEN_SECRET')
LIST_ID = get('LIST_ID')
