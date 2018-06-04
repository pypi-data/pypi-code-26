"""
Base settings for a Django Rest Framework Project
"""


# Create of merge INSTALLED_APPS
# print(globals().get('INSTALLED_APPS', []))
# INSTALLED_APPS = globals().get('INSTALLED_APPS', [])
# print(globals().get('INSTALLED_APPS', []))
DRF_INSTALLED_APPS = [
    'django_filters',
    'crispy_forms',
    'rest_framework',
]


# Rest Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 25,
}
