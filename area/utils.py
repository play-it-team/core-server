#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

import io
import json
import logging
import os
import zipfile
from urllib.request import urlopen

from django.conf import settings as django_settings
from tqdm import tqdm

from area.enums import ContinentEnum
from area.models import City, Continent, Country, Region

logger = logging.getLogger(__name__)


class Geoname(object):
	def __init__(self, quiet=False, force=False):
		self.export_url = {
				'dump': 'http://download.geonames.org/export/dump/',
				'zip':  'http://download.geonames.org/export/zip/'
		}

		self.files = {
				'country':   {
						'file_name': 'countryInfo.txt',
						'urls':      [self.export_url['dump'] + '{file_name}'],
						'fields':    [
								'code',
								'code3',
								'codeNum',
								'fips',
								'name',
								'capital',
								'area',
								'population',
								'continent',
								'tld',
								'currencyCode',
								'currencyName',
								'phone',
								'postalCodeFormat',
								'postalCodeRegex',
								'languages',
								'geonameid',
								'neighbours',
								'equivalentFips'
						]
				},
				'region':    {
						'file_name': 'admin1CodesASCII.txt',
						'urls':      [self.export_url['dump'] + '{file_name}'],
						'fields':    [
								'code',
								'name',
								'asciiName',
								'geonameid'
						]
				},
				'city500':   {
						'file_name': 'cities500.zip',
						'urls':      [self.export_url['dump'] + '{file_name}', ],
						'fields':    [
								'geonameid',
								'name',
								'asciiName',
								'alternateNames',
								'latitude',
								'longitude',
								'featureClass',
								'featureCode',
								'countryCode',
								'cc2',
								'admin1Code',
								'admin2Code',
								'admin3Code',
								'admin4Code',
								'population',
								'elevation',
								'gtopo30',
								'timezone',
								'modificationDate'
						]
				},
				'city1000':  {
						'file_name': 'cities1000.zip',
						'urls':      [self.export_url['dump'] + '{file_name}', ],
						'fields':    [
								'geonameid',
								'name',
								'asciiName',
								'alternateNames',
								'latitude',
								'longitude',
								'featureClass',
								'featureCode',
								'countryCode',
								'cc2',
								'admin1Code',
								'admin2Code',
								'admin3Code',
								'admin4Code',
								'population',
								'elevation',
								'gtopo30',
								'timezone',
								'modificationDate'
						]
				},
				'city15000': {
						'file_name': 'cities15000.zip',
						'urls':      [self.export_url['dump'] + '{file_name}', ],
						'fields':    [
								'geonameid',
								'name',
								'asciiName',
								'alternateNames',
								'latitude',
								'longitude',
								'featureClass',
								'featureCode',
								'countryCode',
								'cc2',
								'admin1Code',
								'admin2Code',
								'admin3Code',
								'admin4Code',
								'population',
								'elevation',
								'gtopo30',
								'timezone',
								'modificationDate'
						]
				}
		}

		self.data_dir = os.path.join(django_settings.MEDIA_ROOT, 'geoname')
		self.quiet = quiet
		self.force = force

	def import_options(self):
		return [
				'continent',
				'country',
				'region',
				'city'
		]

	def __download_file__(self, file_key):
		if 'file_name' in self.files[file_key]:
			file_names = [self.files[file_key]['file_name']]
		else:
			raise Exception("'file_name' key is missing from %s", self.files[file_key])

		for file_name in file_names:
			urls = [e.format(file_name=file_name) for e in self.files[file_key]['urls']]
			content = None
			for url in urls:
				try:
					content = urlopen(url=url)
					if ['text/plain', 'application/zip'] not in content.headers['Content-Type']:
						raise Exception(
								"Content type of downloaded file was {}".format(content.headers['Content-Type']))
					logger.debug("Downloaded: {}".format(url))
				except Exception:
					content = None
					continue

			if content is not None:
				logger.debug("Saving: {}/{}".format(self.data_dir, file_name))
				if not os.path.exists(self.data_dir):
					os.makedirs(self.data_dir)

				with open(os.path.join(self.data_dir, file_name), 'wb') as file:
					file.write(content.read())

			if not os.path.exists(os.path.join(self.data_dir, file_name)):
				raise Exception("File not found and download failed: {} [{}]".format(file_name, url))

	def __get_data__(self, file_key):
		if 'file_name' in self.files[file_key]:
			file_names = [self.files[file_key]['file_name']]
		else:
			file_names = self.files[file_key]['file_names']

		for file_name in file_names:
			name, ext = file_name.rsplit('.', 1)
			logger.debug("Reading: {}/{}".format(self.data_dir, file_name))

			if ext == 'zip':
				file_path = os.path.join(self.data_dir, file_name)
				zip_member = zipfile.ZipFile(file_path).open(name + '.txt', 'r')
				file_obj = io.TextIOWrapper(zip_member, encoding='utf-8')
			else:
				file_obj = io.open(os.path.join(self.data_dir, file_name), 'r', encoding='utf-8')

			for row in file_obj:
				if not row.startswith('#'):
					yield dict(list(zip(self.files[file_key]['fields'], row.rstrip('\n').split('\t'))))

	def import_continent(self):
		if Continent.objects.count() != len(ContinentEnum.choices()) or self.force:
			for continent in tqdm(ContinentEnum.choices(), disable=self.quiet, total=len(ContinentEnum.choices()),
			                      desc="Importing continents"):
				Continent.objects.update_or_create(code=continent[0], defaults={'name': continent[1]})

	def import_country(self):
		file_key = 'country'

		self.__download_file__(file_key=file_key)
		data = self.__get_data__(file_key=file_key)
		total_count = sum(1 for _ in data)
		data = self.__get_data__(file_key=file_key)

		continents = {c.code: c.name for c in Continent.objects.all()}

		if Country.objects.count() != total_count or self.force:
			for item in tqdm(data, disable=self.quiet, total=total_count, desc="Importing countries"):
				try:
					country_id = int(item['geonameid'])
				except KeyError:
					logger.warning('Country has no Geo name ID: %s --skipping' % item['name'])
					continue
				except ValueError:
					logger.warning('Country has non-numeric Geo name ID: %s --skipping' % item['geonameid'])
					continue

				defaults = {
						'name':      item['name'],
						'code':      item['code'],
						'code3':     item['code3'],
						'continent': Continent.objects.get(name=continents[item['continent']]),
						'tld':       item['tld']
				}

				country, created = Country.objects.update_or_create(id=country_id, defaults=defaults)
				logger.debug("%s country '%s'", "Added" if created else "Updated", defaults['name'])

	def __build_country_index__(self):
		self.country_index = {}

		for obj in tqdm(Country.objects.all(), disable=self.quiet, total=Country.objects.count(),
		                desc="Building country index"):
			self.country_index[obj.code] = obj

	def import_region(self):
		file_key = 'region'

		self.__download_file__(file_key=file_key)
		data = self.__get_data__(file_key=file_key)
		self.__build_country_index__()
		total_count = sum(1 for _ in data)
		data = self.__get_data__(file_key=file_key)

		countries_not_found = {}

		if Region.objects.count() != total_count or self.force:
			for item in tqdm(data, disable=self.quiet, total=total_count, desc="Importing regions"):
				try:
					region_id = int(item['geonameid'])
				except KeyError:
					logger.warning('Region has no Geo name ID: %s --skipping' % item['name'])
					continue
				except ValueError:
					logger.warning('Region has non-numeric Geo name ID: %s --skipping' % item['geonameid'])
					continue

				country_code, region_code = item['code'].split('.')

				defaults = {
						'name':      item['name'],
						'asciiName': item['asciiName'],
						'code':      region_code
				}

				try:
					defaults['country'] = self.country_index[country_code]
				except KeyError:
					countries_not_found.setdefault(country_code, []).append(defaults['name'])
					logger.warning("Region: %s: Cannot find country: %s --skipping", defaults['name'], country_code)
					continue

				region, created = Region.objects.update_or_create(id=region_id, defaults=defaults)
				logger.debug("%s region: %s, %s", "Added" if created else "Updated", item['code'], region.__str__())

			if countries_not_found:
				countries_not_found_file = os.path.join(self.data_dir, 'countries_not_found.json')
				try:
					with open(countries_not_found_file, 'w+') as file_pointer:
						json.dump(countries_not_found, fp=file_pointer, sort_keys=True, indent=4)
				except Exception as e:
					logger.warning("Unable to write log file '%s': %s", countries_not_found_file, e)

	def __build_region_index__(self):
		self.region_index = {}
		for obj in tqdm(Region.objects.all(), disable=self.quiet, total=Region.objects.count(),
		                desc="Building region index"):
			self.region_index[obj.full_code()] = obj

	def import_city(self, population=500):
		file_key = 'city{}'.format(population)

		self.__download_file__(file_key=file_key)
		data = self.__get_data__(file_key=file_key)
		self.__build_country_index__()
		self.__build_region_index__()
		total_count = sum(1 for _ in data)
		data = self.__get_data__(file_key=file_key)

		if City.objects.count() != total_count or self.force:
			for item in tqdm(data, disable=self.quiet, total=total_count, desc="Importing cities"):
				try:
					city_id = int(item['geonameid'])
				except KeyError:
					logger.warning('City has no Geo name ID: %s --skipping' % item['name'])
					continue
				except ValueError:
					logger.warning('City has non-numeric Geo name ID: %s --skipping' % item['geonameid'])
					continue

				defaults = {
						'name':      item['name'],
						'asciiName': item['asciiName']
				}

				country_code = item['countryCode']
				try:
					country = Country.objects.get(name=self.country_index[country_code])
					defaults['country'] = country
				except KeyError:
					logger.warning("City: %s: Cannot find country: %s --skipping", item['name'], country_code)
					continue

				region_code = item['admin1Code']
				try:
					region_key = country_code + '.' + region_code
					region = Region.objects.filter(name=self.region_index[region_key]).distinct().first()
					defaults['region'] = region
				except KeyError:
					logger.warning("City: %s: Cannot find region: %s --skipping", item['name'], region_code)
					continue

				city, created = City.objects.update_or_create(id=city_id, defaults=defaults)
				logger.debug("%s city: %s", "Added" if created else "Updated", city.__str__())

	def flush_continent(self):
		logger.info("Flushing continent data")
		Continent.objects.all().delete()

	def flush_country(self):
		logger.info("Flushing country data")
		Country.objects.all().delete()

	def flush_region(self):
		logger.info("Flushing region data")
		Region.objects.all().delete()

	def flush_city(self):
		logger.info("Flushing city data")
		City.objects.all().delete()
