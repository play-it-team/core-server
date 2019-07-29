#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

from django.contrib import admin

from health.models import Event, EventUpdate, Service


# Register your models here.
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
	list_display = ('name', 'get_status', 'description', 'order', 'updated_on')
	search_fields = ('name', 'description')
	prepopulated_fields = {'slug': ('name',)}
	exclude = ('created_on', 'updated_on')

	def get_status(self, obj):
		return obj.get_message()

	get_status.short_description = 'Status'


class EventUpdateInline(admin.StackedInline):
	model = EventUpdate
	extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
	list_display = ('created_on', 'description', 'message', 'get_status', 'updated_on')
	search_fields = ('description', 'message')
	list_filter = ('services',)
	exclude = ('created_on', 'updated_on')
	inlines = [EventUpdateInline]

	def get_status(self, obj):
		return obj.get_message()

	get_status.short_description = 'Status'


@admin.register(EventUpdate)
class EventUpdateAdmin(admin.ModelAdmin):
	list_display = ('created_on', 'message', 'status', 'event')
	search_fields = ('message',)
	exclude = ('created_on', 'updated_on')
