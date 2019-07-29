#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

import six
from django.conf import settings
from django.contrib import admin
from django.template.loader import render_to_string

from account.models import Account, Avatar
from account.signals import avatar_updated


# Register your models here.
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
	list_display = ('user',)


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
	list_display = ('get_avatar', 'account', 'primary', 'uploaded_on')
	list_filter = ('primary',)
	exclude = ('uploaded_on',)

	def get_avatar(self, obj):
		try:
			context = dict({
					'url':  obj.get_absolute_url(),
					'alt':  six.text_type(obj.account),
					'size': settings.AVATAR_DEFAULT_SIZE
			})
		except ValueError:
			context = dict({
					'url':  None,
					'alt':  six.text_type(obj.account),
					'size': settings.AVATAR_DEFAULT_SIZE
			})

		return render_to_string('account/avatar_tag.html', context)

	def save_model(self, request, obj, form, change):
		super(AvatarAdmin, self).save_model(request, obj, form, change)
		avatar_updated.send(sender=Avatar, account=request.user, avatar=obj)
