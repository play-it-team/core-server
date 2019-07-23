#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

from django.contrib.gis.db import models


# Create your models here.
class Continent(models.Model):
	code = models.CharField(max_length=2, primary_key=True, db_index=True)
	name = models.CharField(max_length=64, db_index=True)

	class Meta:
		ordering = ['name']
		verbose_name = 'Continent'
		verbose_name_plural = 'Continents'

	def __str__(self):
		return self.name


class Country(models.Model):
	id = models.CharField(max_length=64, db_index=True, primary_key=True)
	name = models.CharField(max_length=64, db_index=True)
	code = models.CharField(max_length=2, db_index=True, unique=True)
	code3 = models.CharField(max_length=3, db_index=True, unique=True)
	continent = models.ForeignKey(to=Continent, null=True, related_name='countries', on_delete=models.SET_NULL)
	tld = models.CharField(max_length=5)

	class Meta:
		ordering = ['name']
		verbose_name = 'Country'
		verbose_name_plural = 'Countries'

	def __str__(self):
		return self.name


class Region(models.Model):
	id = models.CharField(max_length=64, db_index=True, primary_key=True)
	code = models.CharField(max_length=64, db_index=True)
	name = models.CharField(max_length=64, db_index=True)
	asciiName = models.CharField(max_length=64, db_index=True)
	country = models.ForeignKey(to=Country, related_name='regions', on_delete=models.CASCADE)

	class Meta:
		ordering = ['name']
		unique_together = (('country', 'name'))
		verbose_name = 'Region'
		verbose_name_plural = 'Regions'

	def __str__(self):
		return self.name if self.name else self.asciiName

	@property
	def parent(self):
		return self.country

	def full_code(self):
		return ".".join([self.parent.code, self.code])


class City(models.Model):
	id = models.CharField(max_length=64, db_index=True, primary_key=True)
	name = models.CharField(max_length=200, db_index=True)
	asciiName = models.CharField(max_length=200, db_index=True)
	country = models.ForeignKey(to=Country, related_name='cities', on_delete=models.CASCADE)
	region = models.ForeignKey(to=Region, related_name='cities', on_delete=models.CASCADE, null=True, blank=True)
	location = models.PointField(null=True, blank=True)

	class Meta:
		ordering = ['name']
		unique_together = ('country', 'region', 'id', 'name')
		verbose_name = 'City'
		verbose_name_plural = 'Cities'

	def __str__(self):
		return self.name if self.name else self.asciiName

	@property
	def parent(self):
		return self.region
