#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

import logging

from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import signals
from django.utils import six
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from PIL import Image

from account.enums import AccountGender, AvatarSizeEnum
from account.fields import AvatarField
from account.utils import avatar_file_path, find_extension

logger = logging.getLogger(__name__)


# Create your models here.
class Account(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='account', verbose_name=_('User'),
	                            on_delete=models.CASCADE)
	dob = models.DateField(verbose_name=_('Date of Birth'), null=True, blank=True)
	gender = models.CharField(max_length=1, verbose_name=_('Gender'), choices=AccountGender.choices(), null=True,
	                          blank=True)

	def __str__(self):
		return str(self.user)


class Avatar(models.Model):
	account = models.ForeignKey(to=Account, related_name='avatar', verbose_name=_("Account"), on_delete=models.CASCADE)
	primary = models.BooleanField(verbose_name=_("Primary"), default=False)
	avatar = AvatarField(verbose_name=_("Avatar"))
	uploaded_on = models.DateTimeField(verbose_name=_("Uploaded on"), default=now)

	class Meta:
		verbose_name = _("Avatar")
		verbose_name_plural = _("Avatars")

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		avatars = Avatar.objects.filter(account=self.account)
		if self.pk:
			avatars = avatars.exclude(pk=self.pk)
		if settings.AVATAR_MAX_PER_USER > 1:
			if self.primary:
				avatars = avatars.filter(primary=True)
				avatars.update(primary=True)
		else:
			avatars.delete()
		super(Avatar, self).save(force_insert, force_update, using, update_fields)

	def transpose_image(self, image):
		exif_orientation_steps = {
				1: [],
				2: ['FLIP_LEFT_RIGHT'],
				3: ['ROTATE_360'],
				4: ['FLIP_TOP_BOTTOM'],
				5: ['ROTATE_270', 'FLIP_LEFT_RIGHT'],
				6: ['ROTATE_270'],
				7: ['ROTATE_90', 'FLIP_LEFT_RIGHT'],
				8: ['ROTATE_90']
		}
		try:
			orientation = image._getexif()[0x0112]
			ops = exif_orientation_steps[orientation]
		except TypeError:
			ops = []

		for method in ops:
			image = image.transpose(getattr(Image, method))

		return image

	def create_thumbnail(self, size, quality=None):
		try:
			avatar_file = self.avatar.storage.open(self.avatar.name, 'rb')
			image = Image.open(avatar_file)
			image = self.transpose_image(image)
			quality = quality or settings.AVATAR_THUMB_QUALITY
			width, height = image.size
			if width != size or height != size:
				if width > height:
					diff = int((width - height) / 2)
					image = image.crop((diff, 0, width - diff, height))
				else:
					diff = int((height - width) / 2)
					image = image.crop((0, diff, width, height - diff))
				if image.mode not in ['RGB', 'RGBA']:
					image.convert('RGB')
				image = image.resize((size, size), settings.AVATAR_RESIZE_METHOD)
				thumb = six.BytesIO()
				image.save(thumb, settings.AVATAR_THUMB_FORMAT, quality=quality)
				thumb_file = ContentFile(thumb.getvalue())
			else:
				thumb_file = File(avatar_file)
			self.avatar.storage.save(self.avatar_name(size), thumb_file)
		except IOError:
			pass

	def avatar_name(self, size):
		ext = find_extension(fmt=settings.AVATAR_THUMB_FORMAT)
		return avatar_file_path(instance=self, size=size, ext=ext)

	def thumbnail_exists(self, size):
		return self.avatar.storage.exists(self.avatar_name(size=size))

	def avatar_url(self, size):
		return self.avatar.storage.url(self.avatar_name(size=size))

	def get_absolute_url(self):
		return self.avatar_url(settings.AVATAR_DEFAULT_SIZE)


def create_default_thumbnail(sender, instance, created=False, **kwargs):
	for size in AvatarSizeEnum.__iter__():
		instance.create_thumbnail(size.value)
	instance.create_thumbnail(settings.AVATAR_DEFAULT_SIZE)


def remove_avatar_images(instance=None, **kwargs):
	for size in AvatarSizeEnum.__iter__():
		if instance.thumbnail_exists(size=size.value):
			instance.avatar.storage.delete(instance.avatar_name(size=size.value))
	if instance.thumbnail_exists(size=settings.AVATAR_DEFAULT_SIZE):
		instance.avatar.storage.delete(instance.avatar_name(size=settings.AVATAR_DEFAULT_SIZE))
	try:
		instance.avatar.storage.delete(instance.avatar.name)
	except AssertionError:
		logger.warning("Avatar file not found for user: %s", instance.account)
		pass


def user_post_save(**kwargs):
	if kwargs.get("raw", False):
		return False

	user, user_created = kwargs['instance'], kwargs['created']
	if user_created:
		Account(user=user).save()


signals.post_save.connect(user_post_save, sender=settings.AUTH_USER_MODEL)
signals.post_save.connect(create_default_thumbnail, sender=Avatar)
if settings.AVATAR_CLEANUP_DELETED:
	signals.post_delete.connect(remove_avatar_images, sender=Avatar)
