#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

from .base import *

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
		'default': {
				'ENGINE':   config('DB_ENGINE', cast=str),
				'NAME':     config('DB_NAME', cast=str),
				'USER':     config('DB_USER', cast=str),
				'PASSWORD': config('DB_PASSWORD', cast=str, default=''),
				'HOST':     config('DB_HOST', cast=str),
				'PORT':     config('DB_PORT', cast=str)
		}
}
