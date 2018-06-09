from importlib import import_module
from django.conf import settings

# Re-exporting for unified settings import
AUTH_USER_MODEL = settings.AUTH_USER_MODEL


def static_limiter(user):
    return getattr(settings, 'USER_IMAGES_LIMIT', 10000000)


lim_p, lim_m = getattr(settings,
                       'USER_IMAGES_LIMITER',
                       'django_user_images.settings.static_limiter'
                       ).rsplit('.', 1)

LIMITER = getattr(import_module(lim_p), lim_m)
FILE_LIMIT = getattr(settings, 'USER_IMAGE_ONE_FILE_LIMIT', 100000)
