#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors
import logging

from django.core.management.base import BaseCommand

from area.utils import Geoname

logger = logging.getLogger(__name__)


class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument(
				'--force',
				action='store_true',
				default=False,
				dest='force',
				help='Import even if files are up-to-date'
		)

		parser.add_argument(
				'--flush',
				default='',
				dest='flush',
				help='Flush data from the database'
		)

		parser.add_argument(
				'--import',
				default='',
				dest='import',
				help='Selectively import data into the database'
		)

		parser.add_argument(
				'--quiet',
				action='store_true',
				default=False,
				dest='quiet',
				help='Hide progress bar'
		)

	def handle(self, *args, **options):
		self.options = options
		self.force = self.options['force']
		self.flush = self.options['flush']
		self.imports = self.options['import']
		self.quiet = self.options['quiet']

		geoname = Geoname(quiet=self.quiet, force=self.force)

		self.flushes = [e for e in self.flush.split(',') if e]
		if 'all' in self.flushes:
			self.flushes = geoname.import_options()
		for flush in self.flushes:
			func = getattr(geoname, "flush_" + flush)
			func()

		self.imports = [e for e in self.imports.split(',') if e]
		if 'all' in self.imports:
			self.imports = geoname.import_options()
		if self.flushes:
			self.imports = []
		for imports in self.imports:
			func = getattr(geoname, "import_" + imports)
			func()
