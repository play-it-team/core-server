#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors
from rest_framework.permissions import DjangoObjectPermissions


class CommonObjectPermissions(DjangoObjectPermissions):
	perms_map = {
			'GET':     ['%(app_label)s.view_%(model_name)s'],
			'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
			'HEAD':    ['%(app_label)s.view_%(model_name)s'],
			'POST':    ['%(app_label)s.view_%(model_name)s'],
			'PUT':     ['%(app_label)s.view_%(model_name)s'],
			'PATCH':   ['%(app_label)s.view_%(model_name)s'],
			'DELETE':  ['%(app_label)s.view_%(model_name)s']
	}
