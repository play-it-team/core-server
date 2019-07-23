#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

from django.contrib import admin

from artist.models import Artist


# Register your models here.
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
	list_display = ('id', 'name')
	list_display_links = None

	def has_add_permission(self, request):
		return False
