#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors
from django.utils.translation import ugettext_lazy as _


class HealthCheckException(Exception):
	message_type = _('Unknown Exception')

	def __init__(self, message):
		self.message = message

	def __str__(self):
		return _('%s: %s' % (self.message_type, self.message))


class ServiceWarning(HealthCheckException):
	message_type = _('Warning')


class ServiceUnavailable(HealthCheckException):
	message_type = _('Unavailable')


class ServiceReturnedUnexpectedResult(HealthCheckException):
	message_type = _('Unexpected Result')
