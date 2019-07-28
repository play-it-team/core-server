#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

import binascii
import hashlib
import logging
import os

from django.conf import settings
from django.utils.encoding import force_bytes, force_text
from django.utils.module_loading import import_string

logger = logging.getLogger(__name__)


def avatar_path_handler(instance=None, file_name=None, size=None, ext=None):
	# Get the default avatar storage directory
	storage_dir = [settings.AVATAR_STORAGE_DIR]

	if settings.AVATAR_HASH_USERDIRNAMES:
		# Create a hash from username
		tmp = hashlib.md5(force_bytes(instance.account.user.username)).hexdigest()

		# Get the index 0 and 1 and extend that to the storage directory
		storage_dir.extend(tmp[0:2])
	if settings.AVATAR_EXPOSE_USERNAME:
		# Append the username to the directory
		storage_dir.append(instance.account.user.username)
	else:
		# Append the primary key to the directory
		storage_dir.append(force_text(instance.account.user.pk))
	if not file_name:
		# Get the file name from the avatar
		file_name = instance.avatar.name
		if ext:
			# Get the file path and replace the extension with the provided one
			root, old_ext = os.path.splitext(file_name)
			file_name = root + "." + ext
	else:
		if settings.AVATAR_HASH_FILENAMES:
			# Get the file path and extension
			root, ext = os.path.splitext(file_name)
			if settings.AVATAR_RANDOMIZE_HASHNAMES:
				# Generate a random hashed file name
				file_name = binascii.hexlify(os.urandom(16)).decode('ascii')
			else:
				# Generate a MD5 hashed file name
				file_name = hashlib.md5(force_bytes(file_name)).hexdigest()
			# Get the final file name with extension
			file_name = file_name + ext
	if size:
		# Size is provided, create directory named 'resized' with the sub-directories with the size
		storage_dir.extend(['resized', str(size)])
	# Appends the file name to the list that contains the directory structure
	storage_dir.append(os.path.basename(file_name))

	return os.path.join(*storage_dir)


avatar_file_path = import_string(settings.AVATAR_PATH_HANDLER)


def find_extension(fmt):
	fmt = fmt.lower()

	if fmt == 'jpeg':
		fmt = 'jpg'

	return fmt
