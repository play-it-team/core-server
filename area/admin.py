#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from area.models import City, Continent, Country, Region


# Register your models here.

@admin.register(Continent)
class ContinentAdmin(admin.ModelAdmin):
	list_display = ('code', 'name')
	list_display_links = None

	def has_add_permission(self, request):
		return False


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
	list_display = ('code', 'code3', 'name', 'continent', 'tld',)
	list_display_links = None

	def has_add_permission(self, request):
		return False


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
	list_display = ('code', 'name', 'asciiName', 'country')
	list_display_links = None

	def has_add_permission(self, request):
		return False


@admin.register(City)
class CityAdmin(OSMGeoAdmin):
	list_display = ('name', 'asciiName', 'country', 'region', 'location')
	list_display_links = ('name',)

	def has_add_permission(self, request):
		return False
