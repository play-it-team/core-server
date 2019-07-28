#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors
import logging
import tempfile

from django.core.files.base import File
from minio import error as merr

logger = logging.getLogger(__name__)


class ReadOnlyMixin(object):
	"""File class mixin which disallows .write() calls"""

	def writable(self):
		return False

	def write(*args, **kwargs):
		raise NotImplementedError('this is a read only file')


class MinioStorageFile(File):
	def __init__(self, name, mode, storage, **kwargs):
		self._storage = storage
		self.name = name
		self._mode = mode
		self.obj = storage._client.get_object(self._storage._bucket, name)
		self._file = None


class ReadOnlySpooledTemporaryFile(MinioStorageFile, ReadOnlyMixin):
	"""A django File class which buffers the minio object into a local
SpooledTemporaryFile. """
	max_memory_size = 1024 * 1024 * 10

	def __init__(self, name, mode, storage, max_memory_size=None, **kwargs):
		if mode.find("w") > -1:
			raise NotImplementedError(
					"ReadOnlySpooledTemporaryFile storage only support read modes")
		if max_memory_size is not None:
			self.max_memory_size = max_memory_size
		super(ReadOnlySpooledTemporaryFile, self).__init__(name, mode, storage)

	def _get_file(self):
		if self._file is None:
			try:
				obj = self._storage._client.get_object(
						self._storage._bucket, self.name)
				self._file = tempfile.SpooledTemporaryFile(
						max_size=self.max_memory_size)
				for d in obj.stream(amt=1024 * 1024):
					self._file.write(d)
				self._file.seek(0)
				return self._file
			except merr.ResponseError as error:
				raise merr.ResponseError(
						"File {} does not exist".format(self.name), error)
			finally:
				try:
					obj.release_conn()
				except Exception as e:
					logger.error(str(e))
		return self._file

	def _set_file(self, value):
		self._file = value

	file = property(_get_file, _set_file)

	def close(self):
		if self._file is not None:
			self._file.close()
			self._file = None
