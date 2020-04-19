#  Copyright (c) 2019 - 2020. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

import six
from django.conf import settings
from django.contrib import admin
from django.template.loader import render_to_string

from account.models import Account, AccountDeletion, EmailAddress, PasswordExpiry, PasswordHistory, SignupCode, Avatar
from account.signals import avatar_updated


# Register your models here.
@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ('get_avatar', 'account', 'primary', 'uploaded_on')
    list_filter = ('primary',)
    exclude = ('uploaded_on',)

    def get_avatar(self, obj):
        try:
            context = dict({
                'url': obj.get_absolute_url(),
                'alt': six.text_type(obj.account),
                'size': settings.AVATAR_DEFAULT_SIZE
            })
        except ValueError:
            context = dict({
                'url': None,
                'alt': six.text_type(obj.account),
                'size': settings.AVATAR_DEFAULT_SIZE
            })

        return render_to_string('account/avatar_tag.html', context)

    def save_model(self, request, obj, form, change):
        super(AvatarAdmin, self).save_model(request, obj, form, change)
        avatar_updated.send(sender=Avatar, account=request.user, avatar=obj)


class SignupCodeAdmin(admin.ModelAdmin):
    list_display = ["code", "max_uses", "use_count", "expiry", "created"]
    search_fields = ["code", "email"]
    list_filter = ["created"]
    raw_id_fields = ["inviter"]


class AccountAdmin(admin.ModelAdmin):
    raw_id_fields = ["user"]


class AccountDeletionAdmin(AccountAdmin):
    list_display = ["email", "date_requested", "date_expunged"]


class EmailAddressAdmin(AccountAdmin):
    list_display = ["user", "email", "verified", "primary"]
    search_fields = ["email", "user__username"]


class PasswordExpiryAdmin(admin.ModelAdmin):
    raw_id_fields = ["user"]


class PasswordHistoryAdmin(admin.ModelAdmin):
    raw_id_fields = ["user"]
    list_display = ["user", "timestamp"]
    list_filter = ["user"]
    ordering = ["user__username", "-timestamp"]


admin.site.register(Account, AccountAdmin)
admin.site.register(SignupCode, SignupCodeAdmin)
admin.site.register(AccountDeletion, AccountDeletionAdmin)
admin.site.register(EmailAddress, EmailAddressAdmin)
admin.site.register(PasswordExpiry, PasswordExpiryAdmin)
admin.site.register(PasswordHistory, PasswordHistoryAdmin)
