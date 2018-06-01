SECRET_KEY = '2^mza*qpug3+htv7jxecatc0w&rluw!b#2cf9r*+&3fj8a2i66'
INSTALLED_APPS = [
    "authentication",
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django-generic-rest.db',
    }
}