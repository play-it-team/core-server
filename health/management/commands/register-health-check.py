#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors
import logging

from django.core.management.base import BaseCommand

from health.enums import HealthStatusEnum
from health.models import Service

logger = logging.getLogger(__name__)


class Command(BaseCommand):
	def handle(self, *args, **options):
		# Register Database health check service
		database_defaults = {
				'name':        'Database',
				'description': 'This service checks database connectivity.',
				'status':      HealthStatusEnum.red.name,
				'order':       0
		}
		Service.objects.update_or_create(slug='database', defaults=database_defaults)

		cache_defaults = {
				'name':        'Cache',
				'description': 'This service checks cache functionality.',
				'status':      HealthStatusEnum.red.name,
				'order':       1
		}
		Service.objects.update_or_create(slug='cache', defaults=cache_defaults)

		disk_defaults = {
				'name':        'Disk',
				'description': 'This service checks the disk usage.',
				'status':      HealthStatusEnum.red.name,
				'order':       2
		}
		Service.objects.update_or_create(slug='disk', defaults=disk_defaults)

		memory_defaults = {
				'name':        'Memory',
				'description': 'This service checks the memory usage.',
				'status':      HealthStatusEnum.red.name,
				'order':       3
		}
		Service.objects.update_or_create(slug='memory', defaults=memory_defaults)

		storage_defaults = {
				'name':        'Storage',
				'description': 'This service checks the storage.',
				'status':      HealthStatusEnum.red.name,
				'order':       4
		}
		Service.objects.update_or_create(slug='storage', defaults=storage_defaults)

		celery_defaults = {
				'name':        'Periodic Tasks',
				'description': 'This service checks the periodic tasks functionality.',
				'status':      HealthStatusEnum.red.name,
				'order':       5
		}
		Service.objects.update_or_create(slug='celery', defaults=celery_defaults)

		rabbit_mq_defaults = {
				'name':        'Rabbit MQ',
				'description': 'This service checks the Rabbit MQ server connectivity.',
				'status':      HealthStatusEnum.red.name,
				'order':       6
		}
		Service.objects.update_or_create(slug='rabbit-mq', defaults=rabbit_mq_defaults)
