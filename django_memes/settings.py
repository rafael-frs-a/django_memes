import os
import environ
from pathlib import Path
from django.contrib.messages import constants as messages

env = environ.Env()

APP_NAME = 'Django Memes'
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = env('SECRET_KEY', default='default secret key')
DEBUG = env.bool('DEBUG', False)
ALLOWED_HOSTS = [env('SITE_HOST')]

if DEBUG:
    ALLOWED_HOSTS = ['*']

SITE_URL = env('SITE_URL', default=ALLOWED_HOSTS[0])

INSTALLED_APPS = [
    'base',
    # django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    # 3rd party
    'widget_tweaks',
    'sslserver',
    'django_celery_results',
    # local apps
    'users',
    'emails',
    'posts',
    'moderation',
    'services',
    'pwa',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'base.middleware.HttpResponseNotAllowedMiddleware'
]

ROOT_URLCONF = 'django_memes.urls'

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
                'base.context_processors.global_settings'
            ],
        },
    },
]

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger'
}

WSGI_APPLICATION = 'django_memes.wsgi.application'

DATABASES = {
    'default': env.db('DATABASE_URL'),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'users.backends.LoginBackend'
]

TIME_ZONE = 'UTC'
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
VALID_PROFILE_PIC_FILETYPES = ['jpg', 'jpeg', 'png']
VALID_MEME_FILETYPES = ['jpg', 'jpeg', 'png']
PROFILE_PIC_SIZE = (256, 256)
MEME_SIZE = (500, 700)

POST_WAITING_INTERVAL = 1 * 60 * 60  # 1 hour
POSTS_PER_PAGE = 5
DATE_TIME_DISPLAY_FORMAT = '%d %b %Y, %H:%M'
USER_TEMPORARY_BAN = 24 * 60 * 60  # 24 hours
USER_PERM_BAN_COUNT = 3

LOGIN_URL = '/login/'
AUTH_USER_MODEL = 'users.User'
ACCOUNT_ACTIVATION_EXPIRATION_TIME = 2 * 60 * 60  # 2 hours
RESET_PASSWORD_EXPIRATION_TIME = 15 * 60  # 15 minutes
CHANGE_EMAIL_EXPIRATION_TIME = 15 * 60  # 15 minutes
ACCOUNT_DELETION_INTERVAL = 48 * 60 * 60  # 48 hours

TEST_MODE = False
TEST_RUNNER = 'base.runner.PytestTestRunner'

CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env.int('EMAIL_PORT', 587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', False)
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', False)
EMAIL_FROM = APP_NAME + ' noreply@djangomemes.com'
EMAIL_TEST_USER = env('EMAIL_TEST_USER')
