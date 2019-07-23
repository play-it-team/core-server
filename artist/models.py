#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

from django.db import models


# Create your models here.
class Artist(models.Model):
	id = models.CharField(max_length=200, db_index=True, primary_key=True)
	name = models.CharField(max_length=500, db_index=True)

	class Meta:
		ordering = ['name']
		verbose_name = 'Artist'
		verbose_name_plural = 'Artists'

	def __str__(self):
		return self.name
