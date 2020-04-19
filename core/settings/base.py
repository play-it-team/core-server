#  Copyright (c) 2019 - 2020. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

from PIL import Image
from decouple import config

# Site ID
SITE_ID = 1

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', cast=str)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites'
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'guardian'
]

LOCAL_APPS = [
    'account',
    'area',
    'artist',
    'common',
    'health'
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

DJANGO_SECURITY_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
]

DJANGO_CACHE_MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware'
]

DJANGO_MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.middleware.locale.LocaleMiddleware'
]

MIDDLEWARE = DJANGO_SECURITY_MIDDLEWARE + DJANGO_CACHE_MIDDLEWARE + DJANGO_MIDDLEWARE

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend'
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_DIR, 'templates')],
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

WSGI_APPLICATION = 'core.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', cast=str),
        'NAME': config('DB_NAME', cast=str),
        'USER': config('DB_USER', cast=str),
        'PASSWORD': config('DB_PASSWORD', cast=str, default=''),
        'HOST': config('DB_HOST', cast=str),
        'PORT': config('DB_PORT', cast=str)
    }
}

# Email Settings
EMAIL_HOST = config('EMAIL_HOST', cast=str)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', cast=str)
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', cast=str)
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = config('LANGUAGE_CODE', cast=str)

TIME_ZONE = config('TIME_ZONE', cast=str)

USE_I18N = config('USE_I18N', cast=bool)

USE_L10N = config('USE_L10N', cast=bool)

USE_TZ = config('USE_TZ', cast=bool)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATICFILES_DIRS = (os.path.join(PROJECT_DIR, 'static'),)
STATIC_ROOT = os.path.abspath(os.path.join(PROJECT_DIR, 'staticfiles/'))
MEDIA_ROOT = os.path.abspath(os.path.join(PROJECT_DIR, 'media/'))

MEDIA_LOGS = os.path.abspath(os.path.join(MEDIA_ROOT, 'logs'))

if not os.path.exists(MEDIA_LOGS):
    os.makedirs(MEDIA_LOGS)

if not os.path.exists(STATIC_ROOT):
    os.makedirs(STATIC_ROOT)

for static_dirs in STATICFILES_DIRS:
    if not os.path.exists(static_dirs):
        os.makedirs(static_dirs)

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

AUTH_USER_MODEL = 'auth.User'

# Avatar Setting
AVATAR_DEFAULT_SIZE = config('AVATAR_DEFAULT_SIZE', cast=int)
AVATAR_RESIZE_METHOD = Image.ANTIALIAS
AVATAR_STORAGE_DIR = config('AVATAR_STORAGE_DIR', cast=str)
AVATAR_PATH_HANDLER = config('AVATAR_PATH_HANDLER', cast=str)
AVATAR_GRAVATAR_BASE_URL = config('AVATAR_GRAVATAR_BASE_URL', cast=str)
AVATAR_GRAVATAR_FIELD = config('AVATAR_GRAVATAR_FIELD', cast=str)
AVATAR_GRAVATAR_FORCE_DEFAULT = config('AVATAR_GRAVATAR_FORCE_DEFAULT', cast=bool)
AVATAR_DEFAULT_URL = config('AVATAR_DEFAULT_URL', cast=str)
AVATAR_MAX_PER_USER = config('AVATAR_MAX_PER_USER', cast=int)
AVATAR_MAX_SIZE = config('AVATAR_MAX_SIZE')
AVATAR_THUMB_FORMAT = config('AVATAR_THUMB_FORMAT', cast=str)
AVATAR_THUMB_QUALITY = config('AVATAR_THUMB_QUALITY', cast=int)
AVATAR_HASH_FILENAMES = config('AVATAR_HASH_FILENAMES', cast=bool)
AVATAR_HASH_USERDIRNAMES = config('AVATAR_HASH_USERDIRNAMES', cast=bool)
AVATAR_EXPOSE_USERNAME = config('AVATAR_EXPOSE_USERNAME', cast=bool)
AVATAR_ALLOWED_FILE_EXTS = config('AVATAR_ALLOWED_FILE_EXTS', cast=str)
AVATAR_CLEANUP_DELETED = config('AVATAR_CLEANUP_DELETED', cast=bool)
AVATAR_RANDOMIZE_HASHNAMES = config('AVATAR_RANDOMIZE_HASHNAMES', cast=bool)

# Health Check Setting
HEALTH_CHECK_DISK_USAGE_MAX = config('HEALTH_CHECK_DISK_USAGE_MAX', cast=int)
HEALTH_CHECK_MEMORY_USAGE_MAX = config('HEALTH_CHECK_MEMORY_USAGE_MAX', cast=int)
HEALTH_CHECK_WARNINGS_AS_ERRORS = config('HEALTH_CHECK_WARNINGS_AS_ERRORS', cast=bool)
HEALTH_CHECK_CELERY_TIMEOUT = config('HEALTH_CHECK_CELERY_TIMEOUT', cast=int)

# Account Settings
OPEN_SIGNUP = config('OPEN_SIGNUP', cast=bool)
PASSWORD_EXPIRY = config('PASSWORD_EXPIRY', cast=int)
PASSWORD_USE_HISTORY = config('PASSWORD_USE_HISTORY', cast=bool)
PASSWORD_STRIP = config('PASSWORD_STRIP', cast=bool)
REMEMBER_ME_EXPIRY = config('REMEMBER_ME_EXPIRY', cast=int)
EMAIL_CONFIRMATION_REQUIRED = config('EMAIL_CONFIRMATION_REQUIRED', cast=bool)
EMAIL_CONFIRMATION_EMAIL = config('EMAIL_CONFIRMATION_EMAIL', cast=bool)
EMAIL_CONFIRMATION_EXPIRE_DAYS = config('EMAIL_CONFIRMATION_EXPIRE_DAYS', cast=int)
EMAIL_CONFIRMATION_AUTO_LOGIN = config('EMAIL_CONFIRMATION_AUTO_LOGIN', cast=bool)
NOTIFY_ON_PASSWORD_CHANGE = config('NOTIFY_ON_PASSWORD_CHANGE', cast=bool)
DELETION_EXPUNGE_HOURS = config('DELETION_EXPUNGE_HOURS', cast=int)

# Rest Framework Setting
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework_guardian.filters.DjangoObjectPermissionsFilter'
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/day',
        'user': '1000/day'
    },
    'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_PERMISSION_CLASSES': [
        'common.permissions.CommonObjectPermissions'
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
}

ANONYMOUS_USER_NAME = None
