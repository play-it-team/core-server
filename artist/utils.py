#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

import io
import logging
import os
from urllib.request import urlopen

from django.conf import settings as django_settings
from tqdm import tqdm

from artist.models import Artist

logger = logging.getLogger(__name__)


class Artists(object):
	def __init__(self, quiet=False, force=False):
		self.export_url = {
				'additional': 'http://millionsongdataset.com/sites/default/files/AdditionalFiles/'
		}

		self.files = {
				'artist': {
						'file_name': 'unique_artists.txt',
						'urls':      [self.export_url['additional'] + '{file_name}'],
						'fields':    [
								'artist_id',
								'artist_mbid',
								'track_id',
								'artist_name'
						]
				}
		}

		self.data_dir = os.path.join(django_settings.MEDIA_ROOT, 'msd')
		self.file_key = 'artist'
		self.quiet = quiet
		self.force = force

	def __download_file__(self):
		if 'file_name' in self.files[self.file_key]:
			file_names = [self.files[self.file_key]['file_name']]
		else:
			raise Exception("'file_name' key is missing from %s", self.files[self.file_key])

		for file_name in file_names:
			urls = [e.format(file_name=file_name) for e in self.files[self.file_key]['urls']]
			content = None
			url = None

			for url in urls:
				try:
					content = urlopen(url=url)
					if content.headers['Content-Type'] not in ['text/plain']:
						raise Exception("content type of downloaded file was %s", content.headers['Content-Type'])
					logger.debug("Downloaded: %s", url)
				except Exception as e:
					logger.warning(e)
					content = None
					continue

			if content is not None:
				logger.debug("Saving: %s/%s", self.data_dir, file_name)
				if not os.path.exists(self.data_dir):
					os.makedirs(self.data_dir)

				with open(os.path.join(self.data_dir, file_name), 'wb') as file:
					file.write(content.read())
			if not os.path.exists(os.path.join(self.data_dir, file_name)):
				raise Exception("File not found and download failed: %s [%s]", file_name, url)

	def __get_data__(self):
		if 'file_name' in self.files[self.file_key]:
			file_names = [self.files[self.file_key]['file_name']]
		else:
			raise Exception("'file_name' key is missing from %s", self.files[self.file_key])

		for file_name in file_names:
			logger.debug("Reading: %s/%s", self.data_dir, file_name)

			file_obj = io.open(os.path.join(self.data_dir, file_name), 'r', encoding='utf-8')

			for row in file_obj:
				yield dict(list(zip(self.files[self.file_key]['fields'], row.strip('\n').split('<SEP>'))))

	def import_options(self):
		return ['artist']

	def import_artist(self):
		self.__download_file__()
		data = self.__get_data__()
		total_count = sum(1 for _ in data)
		data = self.__get_data__()

		if Artist.objects.count() != total_count or self.force:
			for item in tqdm(data, disable=self.quiet, total=total_count, desc="Importing artists"):
				artist_id = item['artist_id']

				defaults = {
						'name': item['artist_name']
				}

				artist, created = Artist.objects.update_or_create(id=artist_id, defaults=defaults)
				logger.debug("%s artist '%s'", "Added" if created else "Updated", defaults['name'])
		else:
			logger.info("Database is already up-to-date")

	def flush_artist(self):
		logger.info("Flushing artist data")
		Artist.objects.all().delete()
