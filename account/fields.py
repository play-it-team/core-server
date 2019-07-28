#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

from django.conf import settings
from django.core.files.storage import get_storage_class
from django.db import models

from account.utils import avatar_file_path

avatar_storage = get_storage_class(settings.DEFAULT_FILE_STORAGE)()


class AvatarField(models.ImageField):
	def __init__(self, *args, **kwargs):
		super(AvatarField, self).__init__(*args, **kwargs)

		self.max_length = 1024
		self.upload_to = avatar_file_path
		self.storage = avatar_storage
		self.blank = True

	def deconstruct(self):
		name, path, args, kwargs = super(models.ImageField, self).deconstruct()
		return name, path, (), {}
