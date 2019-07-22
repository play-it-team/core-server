#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

from django.test import TestCase

from area.enums import ContinentEnum
from area.models import City, Continent, Country, Region
from area.utils import Geoname


class ContinentTestCase(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.geoname = Geoname(quiet=False, force=True)
		cls.geoname.import_continent()
		cls.continent = Continent.objects.first()

	def test_verbose_plural(self):
		self.assertEqual(str(Continent._meta.verbose_name_plural), "Continents")

	def test_str(self):
		self.assertEqual(str(self.continent), self.continent.name)

	def test_code(self):
		self.assertEqual(str(ContinentEnum.__getitem__(self.continent.code).name), self.continent.code)


class CountryTestCase(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.geoname = Geoname(quiet=False, force=True)
		cls.geoname.import_continent()
		cls.geoname.import_country()
		cls.country = Country.objects.first()

	def test_verbose_plural(self):
		self.assertEqual(str(Country._meta.verbose_name_plural), "Countries")

	def test_str(self):
		self.assertEqual(str(self.country), self.country.name)


class RegionTestCase(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.geoname = Geoname(quiet=False, force=True)
		cls.geoname.import_continent()
		cls.geoname.import_country()
		cls.geoname.import_region()
		cls.region = Region.objects.first()

	def test_verbose_plural(self):
		self.assertEqual(str(Region._meta.verbose_name_plural), 'Regions')

	def test_str(self):
		if self.region.name:
			self.assertEqual(str(self.region), self.region.name)
		else:
			self.assertEqual(str(self.region), self.region.asciiName)

	def test_parent(self):
		self.assertEqual(self.region.parent, self.region.country)

	def test_full_code(self):
		self.assertEqual(str(self.region.full_code()), str(self.region.parent.code + '.' + self.region.code))


class CityTestCase(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.geoname = Geoname(quiet=False, force=True)
		cls.geoname.import_continent()
		cls.geoname.import_country()
		cls.geoname.import_region()
		cls.geoname.import_city(population=15000)
		cls.city = City.objects.first()

	def test_verbose_plural(self):
		self.assertEqual(str(self.city), self.city.name)

	def test_str(self):
		if self.city.name:
			self.assertEqual(str(self.city), self.city.name)
		else:
			self.assertEqual(str(self.city), self.city.asciiName)

	def test_parent(self):
		self.assertEqual(self.city.parent, self.city.region)


class GeonameTestCase(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.geoname = Geoname(quiet=False, force=True)

	def test_import_options(self):
		self.assertListEqual(self.geoname.import_options(), ['continent', 'country', 'region', 'city'])
