#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from health.enums import HealthStatusEnum

HEALTH_STATUS_CHOICE = (
		(0, 'No Problems'),
		(1, 'Minor Issues'),
		(2, ''),
		(3, '')
)


# Create your models here.
class Service(models.Model):
	name = models.CharField(max_length=128, verbose_name=_('Name'))
	slug = models.SlugField(max_length=128, unique=True, verbose_name=_('Slug'))
	description = models.TextField(verbose_name=_('Description'), null=True, blank=True)
	status = models.CharField(max_length=10, verbose_name=_('Status'), choices=HealthStatusEnum.choices(),
	                          default=HealthStatusEnum.green.name)
	order = models.SmallIntegerField(default=0, verbose_name=_('Order'))
	created_on = models.DateTimeField(auto_now=True, verbose_name=_('Created On'))
	updated_on = models.DateTimeField(auto_now_add=True, verbose_name=_('Updated On'))

	class Meta:
		verbose_name = _('Service')
		verbose_name_plural = _('Services')
		ordering = ('order', 'name')

	def __str__(self):
		return self.name

	@classmethod
	def handle_event_m2m_save(cls, sender, instance, action, reverse, model, pk_set, **kwargs):
		if not action.startswith('post_'):
			return
		if not pk_set:
			return

		if model is Service:
			for service in Service.objects.filter(pk__in=pk_set):
				service.update_from_event(instance)
		else:
			for event in Event.objects.filter(pk__in=pk_set):
				instance.update_from_event(event)

	@classmethod
	def handle_event_save(cls, instance, **kwargs):
		for service in instance.services.all():
			service.update_from_event(instance)

	def update_from_event(self, event):
		update_queryset = Service.objects.filter(pk=self.pk)
		if event.updated_on > self.updated_on:
			# If the update is newer than the last update to the self
			update_queryset.filter(updated_on__lt=event.updated_on).update(updated_on=event.updated_on)
			self.updated_on = event.updated_on

		if HealthStatusEnum.__getitem__(event.status).value > HealthStatusEnum.__getitem__(self.status).value:
			# If our status is more critical than the current self status, update to match the current
			update_queryset.filter(status__lt=HealthStatusEnum.__getitem__(event.status).value).update(
					status=event.status)
			self.status = event.status
		elif HealthStatusEnum.__getitem__(event.status).value < HealthStatusEnum.__getitem__(self.status).value:
			# If no more events match the current self status, let's update it to the current status
			if not Event.objects.filter(services=self, status=self.status).exclude(pk=event.pk).exists():
				update_queryset.filter(status__gt=HealthStatusEnum.__getitem__(event.status).value).update(
						status=event.status)
				self.status = event.status

	def get_message(self):
		if HealthStatusEnum.__getitem__(self.status).value == 0:
			return 'This service is operating as expected'
		elif HealthStatusEnum.__getitem__(self.status).value == 1:
			return 'This service is experiencing some issues.'
		elif HealthStatusEnum.__getitem__(self.status).value == 2:
			return 'This service is experiencing major outage.'
		elif HealthStatusEnum.__getitem__(self.status).value == 3:
			return 'This service may be unavailable.'


class EventBase(models.Model):
	class Meta:
		abstract = True

	def join_with_and(self, values):
		if len(values) == 2:
			return ' and '.join(values) + ' are'
		elif len(values) > 2:
			return ('%s, and %s' % (', '.join(values[:-1]), values[-1])) + ' are'
		return values[0] + ' is'

	def get_message(self):
		if HealthStatusEnum.__getitem__(self.status).value == 0:
			return _('%s operating as expected.' % self.join_with_and([a[1] for a in self.get_services()]))
		elif HealthStatusEnum.__getitem__(self.status).value == 1:
			return _('%s experiencing some issues.' % self.join_with_and([a[1] for a in self.get_services()]))
		elif HealthStatusEnum.__getitem__(self.status).value == 2:
			return _('%s experiencing major issues.' % self.join_with_and([a[1] for a in self.get_services()]))
		elif HealthStatusEnum.__getitem__(self.status).value == 3:
			return _('%s unavailable.' % self.join_with_and([a[1] for a in self.get_services()]))
		return ''


class Event(EventBase):
	services = models.ManyToManyField(to=Service, verbose_name=_('Service'), related_name='service')
	status = models.CharField(max_length=10, verbose_name=_('Status'), choices=HealthStatusEnum.choices(),
	                          default=HealthStatusEnum.green.name)
	peak_status = models.CharField(max_length=10, verbose_name=_('Peak Status'), choices=HealthStatusEnum.choices(),
	                               default=HealthStatusEnum.green.name)
	description = models.TextField(verbose_name=_('Description'), null=True, blank=True,
	                               help_text='We will auto fill the description from the first event message if not '
	                                         'set')
	message = models.TextField(null=True, blank=True, verbose_name=_('Message'))
	created_on = models.DateTimeField(auto_now=True, verbose_name=_('Created On'))
	updated_on = models.DateTimeField(auto_now_add=True, verbose_name=_('Updated On'))

	class Meta:
		verbose_name = _('Event')
		verbose_name_plural = _('Events')

	def __str__(self):
		return str(self.created_on)

	def get_services(self):
		return self.services.values_list('slug', 'name')

	def get_duration(self):
		return self.updated_on - self.created_on

	@classmethod
	def handle_update_save(cls, instance, created, **kwargs):
		event = instance.event

		if created:
			is_latest = True
		elif EventUpdate.objects.filter(event=event).order_by('-created_on').values_list('event', flat=True)[
			0] == event.pk:
			is_latest = True
		else:
			is_latest = False

		if is_latest:
			update_kwargs = dict(
					status=instance.status,
					updated_on=instance.created_on,
					message=instance.message
			)

			if not event.description:
				update_kwargs['description'] = instance.message

			if not event.peak_status or HealthStatusEnum.__getitem__(
					event.peak_status).value < HealthStatusEnum.__getitem__(instance.status).value:
				update_kwargs['peak_status'] = instance.status

			Event.objects.filter(pk=event.pk).update(**update_kwargs)

			for k, v in update_kwargs.items():
				setattr(event, k, v)

			signals.post_save.send(sender=Event, instance=event, created=False)


class EventUpdate(EventBase):
	event = models.ForeignKey(to=Event, related_name='event', verbose_name=_('Event'), on_delete=models.CASCADE)
	status = models.CharField(max_length=10, verbose_name=_('Status'), choices=HealthStatusEnum.choices())
	message = models.TextField(null=True, blank=True, verbose_name=_('Message'))
	created_on = models.DateTimeField(auto_now=True, verbose_name=_('Created On'))

	class Meta:
		verbose_name = _('Event Update')
		verbose_name_plural = _('Event Updates')

	def __str__(self):
		return str(self.created_on)

	def get_services(self):
		return self.event.services.values_list('slug', 'name')


signals.post_save.connect(Service.handle_event_save, sender=Event)
signals.post_save.connect(Event.handle_update_save, sender=EventUpdate)
signals.m2m_changed.connect(Service.handle_event_m2m_save, sender=Event.services.through)
