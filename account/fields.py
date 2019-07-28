#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

from django.core.files.storage import default_storage
from django.db import models

from account.utils import avatar_file_path


class AvatarField(models.ImageField):
	def __init__(self, *args, **kwargs):
		super(AvatarField, self).__init__(*args, **kwargs)

		self.max_length = 1024
		self.upload_to = avatar_file_path
		self.storage = default_storage
		self.blank = True

	def deconstruct(self):
		name, path, args, kwargs = super(models.ImageField, self).deconstruct()
		return name, path, (), {}
