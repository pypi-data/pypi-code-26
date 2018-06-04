import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if str(os.getenv('DJANGO_DEBUG', 'false')).lower() == 'true' else False

# Store this as a comma delimited list (eg. localhost,127.0.0.1)
ALLOWED_HOSTS = os.environ['DJANGO_ALLOWED_HOSTS'].split(',')


# Create of merge INSTALLED_APPS
# INSTALLED_APPS = globals().get('INSTALLED_APPS', [])
CORE_INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd Party Packages
    'storages',
]


# Django Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Django Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': int(os.environ.get('DB_PORT')) if os.environ.get('DB_PORT') else None,
    },
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# ############################################################################
# T3 Specific Configs
# ############################################################################

# AWS Setup
AWS_STORAGE = False if str(os.getenv('AWS_STORAGE', 'true')).lower() == 'false' else True
if AWS_STORAGE:
    AWS_SERVICE_NAME = os.environ['AWS_SERVICE_NAME']
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
    AWS_AUTO_CREATE_BUCKET = True
    AWS_S3_REGION_NAME = os.environ['AWS_S3_REGION_NAME']

    AWS_S3_OBJECT_PARAMETERS = {
        'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
        'CacheControl': 'max-age=94608000',
    }

    # Default media bucket
    DEFAULT_FILE_STORAGE = 'core.django.storages.MediaStorage'
    MEDIAFILES_BUCKET = os.getenv('AWS_MEDIAFILES_BUCKET', AWS_STORAGE_BUCKET_NAME)
    MEDIAFILES_LOCATION = os.getenv('AWS_MEDIAFILES_LOCATION', AWS_SERVICE_NAME + '/' + 'media')

    # Default static bucket
    STATICFILES_STORAGE = 'core.django.storages.StaticStorage'
    STATICFILES_BUCKET = os.getenv('AWS_STATICFILES_BUCKET', AWS_STORAGE_BUCKET_NAME)
    STATICFILES_LOCATION = os.getenv('AWS_STATICFILES_LOCATION', AWS_SERVICE_NAME + '/' + 'static')
else:
    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    STATIC_URL = '/static/'


# URL Prefix Stuff
URL_PREFIX = os.getenv('URL_PREFIX', '')
if URL_PREFIX != '':
    # Make sure URL_PREFIX ends with a '/'
    if not URL_PREFIX.endswith('/'):
        URL_PREFIX = URL_PREFIX + '/'
    # Make sure URL_PREFIX doesn't start with '/'
    if URL_PREFIX.startswith('/'):
        URL_PREFIX = URL_PREFIX[1:]
