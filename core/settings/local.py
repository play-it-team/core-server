#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

import logging.config

from decouple import Csv

from .base import *

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Logging
# https://docs.djangoproject.com/en/2.2/topics/logging

LOGGING_CONFIG = None
DJANGO_LOG_LEVEL = config('DJANGO_LOG_LEVEL', cast=str)
LOGGING = {
		'version':                  1,
		'disable_existing_loggers': False,
		'formatters':               {
				'verbose': {
						'format':  '%(asctime)s [%(levelname)s] %(module)s %(message)s',
						'datefmt': '%Y-%m-%d %H:%M:%S'
				},
				'simple':  {
						'format': '[%(levelname)s] %(message)s'
				}
		},
		'filters':                  {
				'require_debug_true':  {
						'()': 'django.utils.log.RequireDebugTrue'
				},
				'require_debug_false': {
						'()': 'django.utils.log.RequireDebugFalse'
				}
		},
		'handlers':                 {
				'console':     {
						'level':     'DEBUG',
						'class':     'logging.StreamHandler',
						'formatter': 'simple',
						'filters':   ['require_debug_true']
				},
				'file':        {
						'level':       DJANGO_LOG_LEVEL,
						'class':       'logging.handlers.RotatingFileHandler',
						'filename':    'media/logs/app_{}.log'.format(DJANGO_LOG_LEVEL),
						'formatter':   'verbose',
						'maxBytes':    1024 * 500,
						'backupCount': 5
				},
				'mail_admins': {
						'level':        'ERROR',
						'class':        'django.utils.log.AdminEmailHandler',
						'formatter':    'verbose',
						'include_html': True,
						'filters':      ['require_debug_false']
				}
		},
		'loggers':                  {
				'django': {
						'handlers':  ['console', 'file', 'mail_admins'],
						'propagate': True,
						'level':     'INFO'
				},
				'area':   {
						'handlers':  ['console', 'file', 'mail_admins'],
						'propagate': True,
						'level':     DJANGO_LOG_LEVEL
				},
				'artist': {
						'handlers':  ['console', 'file', 'mail_admins'],
						'propagate': True,
						'level':     DJANGO_LOG_LEVEL
				},
				'common': {
						'handlers':  ['console', 'file', 'mail_admins'],
						'propagate': True,
						'level':     DJANGO_LOG_LEVEL
				}
		}
}

logging.config.dictConfig(LOGGING)
