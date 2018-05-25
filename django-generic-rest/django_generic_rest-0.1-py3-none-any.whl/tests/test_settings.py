SECRET_KEY = '2^mza*qpug3+htv7jxecatc0w&rluw!b#2cf9r*+&3fj8a2i66'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'authentication',
    'tests',
    'generic',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django-generic-rest.db',
    }
}
AUTH_USER_MODEL = 'authentication.User'
USE_TZ = True
ERROR_KEY = 'Error'
ROOT_URLCONF = 'tests.urls'