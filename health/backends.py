#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors
import logging
import socket
import uuid
from timeit import default_timer

import psutil
from amqp.exceptions import AccessRefused
from django.conf import settings
from django.core.cache import cache, CacheKeyWarning
from django.core.files.base import ContentFile
from django.core.files.storage import get_storage_class
from django.db import DatabaseError, IntegrityError
from django.utils.translation import ugettext_lazy as _
from kombu import Connection

from health.exceptions import HealthCheckException, ServiceReturnedUnexpectedResult, ServiceUnavailable, ServiceWarning
from health.models import DatabaseTestModel
from health.tasks import add

logger = logging.getLogger(__name__)


class BaseHealthCheckBackend(object):
	critical_service = True
	"""
	Define is the service is critical to the operation of the site.
	
	If set to ``True`` serivce failures return 500 response code on the health check endpoint
	"""

	def __init__(self):
		self.errors = []

	def check_status(self):
		raise NotImplementedError

	def run_check(self):
		start = default_timer()
		self.errors = []
		try:
			self.check_status()
		except HealthCheckException as e:
			self.add_error(e, e)
		except BaseException:
			logger.exception("Unexpected error")
			raise
		finally:
			self.time_taken = default_timer() - start

	def add_error(self, error, cause=None):
		if isinstance(error, HealthCheckException):
			pass
		elif isinstance(error, str):
			message = error
			error = HealthCheckException(message=message)
		else:
			message = _('Unknown Error')
			error = HealthCheckException(message=message)
		if isinstance(cause, BaseException):
			logger.exception(str(error))
		else:
			logger.error(str(error))
		self.errors.append(error)

	def pretty_status(self):
		if self.errors:
			return "\n".join(str(e) for e in self.errors)
		return _('Working')

	@property
	def status(self):
		return int(not self.errors)

	def identifier(self):
		return self.__class__.__name__


class DatabaseBackend(BaseHealthCheckBackend):
	def check_status(self):
		try:
			obj = DatabaseTestModel.objects.create(name='test')
			obj.name = 'new_test'
			obj.save()
			obj.delete()
		except IntegrityError as e:
			self.add_error(ServiceReturnedUnexpectedResult('Integrity Error'), e)
		except DatabaseError as e:
			self.add_error(ServiceUnavailable('Database Error'), e)


class CacheBackend(BaseHealthCheckBackend):
	critical_service = False

	def check_status(self):
		try:
			cache.set('play_it_health_check', 'working', 1)
			if not cache.get('play_it_health_check') == 'working':
				self.add_error(ServiceUnavailable('Cache key does not match'))
		except CacheKeyWarning as e:
			self.add_error(ServiceReturnedUnexpectedResult('Cache key warning'), e)
		except ValueError as e:
			self.add_error(ServiceReturnedUnexpectedResult('Value Error'), e)
		except ConnectionError as e:
			self.add_error(ServiceReturnedUnexpectedResult('Connection Error'), e)


class DiskUsageBackend(BaseHealthCheckBackend):
	def check_status(self):
		host = socket.gethostname()
		try:
			du = psutil.disk_usage('/')
			disk_usage_max = settings.HEALTH_CHECK_DISK_USAGE_MAX
			if disk_usage_max and du.percent >= disk_usage_max:
				self.add_error(ServiceWarning(('%s %s disk usage exceeds %s%', host, du.percent, disk_usage_max)))
		except ValueError as e:
			self.add_error(ServiceReturnedUnexpectedResult('Value Error'), e)


class MemoryUsageBackend(BaseHealthCheckBackend):
	def check_status(self):
		host = socket.gethostname()
		try:
			memory = psutil.virtual_memory()
			memory_usage = settings.HEALTH_CHECK_MEMORY_USAGE_MAX
			if memory_usage and memory.percent >= memory_usage:
				self.add_error(ServiceWarning(('%s %s memory usage exceeds %s%', host, memory.percent, memory_usage)))
		except ValueError as e:
			self.add_error(ServiceReturnedUnexpectedResult('Value Error'), e)


class CeleryBackend(BaseHealthCheckBackend):
	def check_status(self):
		timeout = settings.HEALTH_CHECK_CELERY_TIMEOUT

		try:
			result = add.apply_async(args=[4, 4], expires=timeout)
			result.get(timeout=timeout)
			if result.result != 8:
				self.add_error(ServiceReturnedUnexpectedResult('Celery returned wrong result'))
		except IOError as e:
			self.add_error(ServiceUnavailable('IOError'), e)
		except NotImplementedError as e:
			self.add_error(ServiceUnavailable('NotImplementedError: Make sure CELERY_RESULT_BACKEND is set'), e)
		except BaseException as e:
			self.add_error(ServiceUnavailable('Unknown Error'), e)


class RabbitMQBackend(BaseHealthCheckBackend):
	def check_status(self):
		logger.debug(_('Checking for a broker URL'))

		broker_url = getattr(settings, 'BROKER_URL', None)

		logger.debug(_('Found %s as the broker URL, connecting to Rabbit MQ server'))

		try:
			with Connection(broker_url) as conn:
				conn.connect()
		except ConnectionRefusedError as e:
			self.add_error(ServiceUnavailable('Unable to connect to Rabbit MQ server: Connection refused'), e)
		except AccessRefused as e:
			self.add_error(ServiceUnavailable('Unable to connect to Rabbit MQ server: Authentication error'), e)
		except IOError as e:
			self.add_error(ServiceUnavailable('IOError'), e)
		except BaseException as e:
			self.add_error(ServiceUnavailable('Unknown Error'), e)
		else:
			logger.debug('Connection established')


class StorageBackend(BaseHealthCheckBackend):
	storage = settings.DEFAULT_FILE_STORAGE

	def get_storage(self):
		if isinstance(self.storage, str):
			return get_storage_class(self.storage)()
		else:
			return self.storage

	def get_file_name(self):
		return 'play_it_health_check/test-%s.txt' % uuid.uuid4()

	def get_file_content(self):
		return 'Working'

	def check_save(self, file_name, file_content):
		storage = self.get_storage()
		file_name = storage.save(file_name, ContentFile(file_content))
		if not storage.exists(file_name):
			self.add_error(ServiceUnavailable('File does not exist'))
		with storage.open(file_name) as f:
			if not f.read() == file_content:
				self.add_error(ServiceUnavailable('File content does not match'))
		return file_name

	def check_delete(self, file_name):
		storage = self.get_storage()
		storage.delete(file_name)
		if storage.exists(file_name):
			self.add_error(ServiceUnavailable('File was not deleted'))

	def check_status(self):
		try:
			file_name = self.get_file_name()
			file_content = self.get_file_content()
			file_name = self.check_save(file_name=file_name, file_content=file_content)
			self.check_delete(file_name)
			return True
		except Exception as e:
			self.add_error(ServiceUnavailable('Unknown Error'), e)
