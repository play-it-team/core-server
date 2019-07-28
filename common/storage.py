#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

import logging
import mimetypes
from datetime import datetime
from time import mktime

import pytz
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from minio import Minio
from minio.error import NoSuchBucket, NoSuchKey, ResponseError

from common.files import ReadOnlySpooledTemporaryFile

logger = logging.getLogger(__name__)


@deconstructible
class MinioStorage(Storage):
	def __init__(self, client, bucket, *args, **kwargs):
		self._client = client
		self._bucket = bucket
		self._file_class = ReadOnlySpooledTemporaryFile

		if self._client:
			if not client.bucket_exists(bucket_name=self._bucket):
				logger.warning("Minio bucket '%s' does not exist, creating...", self._bucket)
				client.make_bucket(bucket_name=self._bucket)

		super(MinioStorage, self).__init__(*args, **kwargs)

	def exists(self, name):
		try:
			return bool(self._client.stat_object(bucket_name=self._bucket, object_name=name))
		except NoSuchKey:
			return False
		except NoSuchBucket:
			return False
		except ValueError:
			return False

	def _save(self, name, content):
		try:
			if hasattr(content, 'seek') and callable(content.seek):
				content.seek(0)
			content_size, content_type, content_name = self._examine_file(name=name, content=content)
			self._client.put_object(bucket_name=self._bucket, object_name=content_name, data=content,
			                        length=content_size, content_type=content_type)
			return content_name
		except ResponseError as e:
			logger.error(e)

	def _examine_file(self, name, content):
		content_size = content.size
		content_type = mimetypes.guess_type(name, strict=False)[0]
		content_name = name

		return content_size, content_type, content_name

	def delete(self, name):
		try:
			self._client.remove_object(bucket_name=self._bucket, object_name=name)
		except ResponseError:
			logger.error("Could not remove file %s", name)

	def get_accessed_time(self, name):
		return self.get_modified_time(name=name)

	def get_created_time(self, name):
		return self.get_modified_time(name=name)

	def get_modified_time(self, name):
		object_info = self._client.stat_object(bucket_name=self._bucket, object_name=name)
		return datetime.fromtimestamp(mktime(object_info.last_modified)).replace(tzinfo=pytz.UTC)

	def size(self, name):
		object_info = self._client.stat_object(bucket_name=self._bucket, object_name=name)
		return object_info.size

	def listdir(self, path):
		return self._client.list_objects(bucket_name=self._bucket, prefix=path)

	def url(self, name):
		return self._client.presigned_url(bucket_name=self._bucket, object_name=name, method='GET')

	def _open(self, name, mode='rb'):
		return self._file_class(name=name, mode=mode, storage=self)

	def path(self, name):
		raise NotImplementedError("This backend doesn't support absolute paths.")


@deconstructible
class MinioMediaStorage(MinioStorage):
	def __init__(self):
		server = settings.MINIO_SERVER
		access_key = settings.MINIO_ACCESS_KEY
		secret_key = settings.MINIO_SECRET_KEY
		media_bucket = settings.MINIO_MEDIA_BUCKET
		secure = settings.MINIO_SECURE

		client = Minio(endpoint=server, access_key=access_key, secret_key=secret_key, secure=secure)

		super(MinioMediaStorage, self).__init__(client=client, bucket=media_bucket)


@deconstructible
class MinioStaticStorage(MinioStorage):
	def __init__(self):
		server = settings.MINIO_SERVER
		access_key = settings.MINIO_ACCESS_KEY
		secret_key = settings.MINIO_SECRET_KEY
		static_bucket = settings.MINIO_STATIC_BUCKET
		secure = settings.MINIO_SECURE

		client = Minio(endpoint=server, access_key=access_key, secret_key=secret_key, secure=secure)

		super(MinioStaticStorage, self).__init__(client=client, bucket=static_bucket)
