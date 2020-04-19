#  Copyright (c) 2019 - 2020. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors


import datetime
import functools
import logging
import operator
from urllib.parse import urlencode

import pytz
import six
from PIL import Image
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.urls import reverse
from django.utils import translation
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from account import signals
from account.enums import AccountGender, AvatarSizeEnum
from account.fields import AvatarField
from account.hooks import hookset
from account.managers import EmailAddressManager, EmailConfirmationManager
from account.utils import avatar_file_path, find_extension
from common.enums import Languages
from common.fields import TimeZoneField
from common.languages import DEFAULT_LANGUAGE

logger = logging.getLogger(__name__)


# Create your models here.
class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='account', verbose_name=_('User'),
                                on_delete=models.CASCADE)
    dob = models.DateField(verbose_name=_('Date of Birth'), null=True, blank=True)
    gender = models.CharField(max_length=1, verbose_name=_('Gender'), choices=AccountGender.choices(), null=True,
                              blank=True)
    language = models.CharField(verbose_name=_("Language"), max_length=10, choices=Languages.choices(),
                                default=DEFAULT_LANGUAGE)
    timezone = TimeZoneField(verbose_name=_("Timezone"))

    def __str__(self):
        return str(self.user)

    @classmethod
    def for_request(cls, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            try:
                return Account._default_manager.get(user=user)
            except Account.DoesNotExist:
                pass
        return AnonymousAccount()

    @classmethod
    def create(cls, request=None, **kwargs):
        create_email = kwargs.pop("create_email", True)
        confirm_email = kwargs.pop("confirm_email", None)
        account = cls(**kwargs)
        if "language" not in kwargs:
            if request is None:
                account.language = DEFAULT_LANGUAGE
            else:
                account.language = translation.get_language_from_request(request, check_path=True)
        account.save()

        if create_email and account.user.email:
            kwargs = {"primary": True}
            if confirm_email is not None:
                kwargs["confirm"] = confirm_email
            EmailAddress.objects.add_email(account.user, account.user.email, **kwargs)

        return account

    def now(self):
        """
        Returns a timezone aware datetime localized to the account's timezone.
        """
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone("UTC"))
        tz = settings.TIME_ZONE if not self.timezone else self.timezone
        return now.astimezone(pytz.timezone(tz))

    def localtime(self, value):
        """
        Given a datetime object as value convert it to the timezone of
        the account.
        """
        tz = settings.TIME_ZONE if not self.timezone else self.timezone
        if value.tzinfo is None:
            value = pytz.timezone(settings.TIME_ZONE).localize(value)
        return value.astimezone(pytz.timezone(tz))


def user_post_save(sender, **kwargs):
    # Disable post_save during manage.py loaddata
    if kwargs.get("raw", False):
        return False

    user, created = kwargs["instance"], kwargs["created"]
    if created:
        Account.create(user=user)


class AnonymousAccount:
    def __init__(self, request=None):
        self.user = AnonymousUser()
        self.timezone = settings.TIME_ZONE
        if request is None:
            self.language = DEFAULT_LANGUAGE
        else:
            self.language = translation.get_language_from_request(request, check_path=True)

    def __str__(self):
        return "AnonymousAccount"


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


class SignupCode(models.Model):
    class AlreadyExists(Exception):
        pass

    class InvalidCode(Exception):
        pass

    code = models.CharField(verbose_name=_("Code"), max_length=64, unique=True)
    max_uses = models.PositiveIntegerField(verbose_name=_("Max Uses"), default=0)
    expiry = models.DateTimeField(verbose_name=_("Expiry"), null=True, blank=True)
    inviter = models.ForeignKey(to=Account, null=True, blank=True, on_delete=models.CASCADE)
    email = models.EmailField(verbose_name=_("Email"), max_length=255, blank=True)
    sent = models.DateTimeField(verbose_name=_("Sent"), blank=True, null=True)
    created = models.DateTimeField(verbose_name=_("Created"), blank=True, default=now, editable=False)
    use_count = models.PositiveIntegerField(verbose_name=_("Use Count"), editable=False, default=0)

    class Meta:
        verbose_name = _("Signup Code")
        verbose_name_plural = _("Signup Codes")

    def __str__(self):
        if self.email:
            return "{0} [{1}]".format(self.email, self.code)
        else:
            return self.code

    @classmethod
    def exists(cls, code=None, email=None):
        checks = []
        if code:
            checks.append(Q(code=code))
        if email:
            checks.append(Q(email=code))
        if not checks:
            return False
        return cls._default_manager.filter(functools.reduce(operator.or_, checks)).exists()

    @classmethod
    def create(cls, **kwargs):
        email, code = kwargs.get("email"), kwargs.get("code")
        if kwargs.get("check_exists", True) and cls.exists(code=code, email=email):
            raise cls.AlreadyExists()
        expiry = now() + datetime.timedelta(hours=kwargs.get("expiry", 24))
        if not code:
            code = hookset.generate_signup_code_token(email)
        params = {
            "code": code,
            "max_uses": kwargs.get("max_uses", 0),
            "expiry": expiry,
            "inviter": kwargs.get("inviter")
        }
        if email:
            params["email"] = email
        return cls(**params)

    @classmethod
    def check_code(cls, code):
        try:
            signup_code = cls._default_manager.get(code=code)
        except cls.DoesNotExist:
            raise cls.InvalidCode()
        else:
            if signup_code.max_uses and signup_code.max_uses <= signup_code.use_count:
                raise cls.InvalidCode()
            else:
                if signup_code.expiry and now() > signup_code.expiry:
                    raise cls.InvalidCode()
                else:
                    return signup_code

    def calculate_use_count(self):
        self.use_count = self.signupcoderesult_set.count()
        self.save()

    def use(self, user):
        """
        Add a SignupCode result attached to the given user.
        """
        result = SignupCodeResult()
        result.signup_code = self
        result.user = user
        result.save()
        hookset.signup_code_used.send(sender=result.__class__, signup_code_result=result)

    def send(self, **kwargs):
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        current_site = kwargs["site"] if "site" in kwargs else Site.objects.get_current()
        if "signup_url" not in kwargs:
            signup_url = "{0}://{1}{2}?{3}".format(
                protocol,
                current_site.domain,
                reverse("account_signup"),
                urlencode({"code": self.code})
            )
        else:
            signup_url = kwargs["signup_url"]
        ctx = {
            "signup_code": self,
            "current_site": current_site,
            "signup_url": signup_url,
        }
        ctx.update(kwargs.get("extra_ctx", {}))
        hookset.send_invitation_email([self.email], ctx)
        self.sent = now()
        self.save()
        hookset.signup_code_sent.send(sender=SignupCode, signup_code=self)


class SignupCodeResult(models.Model):
    signup_code = models.ForeignKey(to=SignupCode, on_delete=models.CASCADE)
    user = models.ForeignKey(to=Account, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now)

    def save(self, **kwargs):
        super(SignupCodeResult, self).save(**kwargs)
        self.signup_code.calculate_use_count()


class EmailAddress(models.Model):
    user = models.ForeignKey(to=Account, on_delete=models.CASCADE)
    email = models.EmailField(max_length=254, unique=True)
    verified = models.BooleanField(verbose_name=_("Verified"), default=False)
    primary = models.BooleanField(verbose_name=_("Primary"), default=False)

    objects = EmailAddressManager()

    class Meta:
        verbose_name = _("Email Address")
        verbose_name_plural = _("Email Addresses")
        unique_together = [("user", "email")]

    def __str__(self):
        return "{0} ({1})".format(self.email, self.user)

    def set_as_primary(self, conditional=False):
        old_primary = EmailAddress.objects.get_primary(self.user)
        if old_primary:
            if conditional:
                return False
            old_primary.primary = False
            old_primary.save()
        self.primary = True
        self.save()
        self.user.email = self.email
        self.user.save()
        return True

    def send_confirmation(self, **kwargs):
        confirmation = EmailConfirmation.create(self)
        confirmation.send(**kwargs)
        return confirmation

    def change(self, new_email, confirm=True):
        """
        Given a new email address, change self and re-confirm.
        """
        with transaction.atomic():
            self.user.email = new_email
            self.user.save()
            self.email = new_email
            self.verified = False
            self.save()
            if confirm:
                self.send_confirmation()


class EmailConfirmation(models.Model):
    email_address = models.ForeignKey(to=EmailAddress, on_delete=models.CASCADE)
    created = models.DateTimeField(default=now)
    sent = models.DateTimeField(null=True)
    key = models.CharField(max_length=64, unique=True)

    objects = EmailConfirmationManager()

    class Meta:
        verbose_name = _("Email Confirmation")
        verbose_name_plural = _("Email Confirmations")

    def __str__(self):
        return "Confirmation for {0}".format(self.email_address)

    @classmethod
    def create(cls, email_address):
        key = hookset.generate_email_confirmation_token(email_address.email)
        return cls._default_manager.create(email_address=email_address, key=key)

    def key_expired(self):
        expiration_date = self.sent + datetime.timedelta(days=settings.ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS)
        return expiration_date <= now()

    key_expired.boolean = True

    def confirm(self):
        if not self.key_expired() and not self.email_address.verified:
            email_address = self.email_address
            email_address.verified = True
            email_address.set_as_primary(conditional=True)
            email_address.save()
            signals.email_confirmed.send(sender=self.__class__, email_address=email_address)
            return email_address

    def send(self, **kwargs):
        current_site = kwargs["site"] if "site" in kwargs else Site.objects.get_current()
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        activate_url = "{0}://{1}{2}".format(
            protocol,
            current_site.domain,
            reverse(settings.ACCOUNT_EMAIL_CONFIRMATION_URL, args=[self.key])
        )
        ctx = {
            "email_address": self.email_address,
            "user": self.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": self.key,
        }
        hookset.send_confirmation_email([self.email_address.email], ctx)
        self.sent = now()
        self.save()
        signals.email_confirmation_sent.send(sender=self.__class__, confirmation=self)


class AccountDeletion(models.Model):
    user = models.ForeignKey(to=Account, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.EmailField(max_length=254)
    date_requested = models.DateTimeField(verbose_name=_("Date Requested"), default=now)
    date_expunged = models.DateTimeField(verbose_name=_("Date Expunged"), null=True, blank=True)

    class Meta:
        verbose_name = _("Account Deletion")
        verbose_name_plural = _("Account Deletions")

    @classmethod
    def expunge(cls, hours_ago=None):
        if hours_ago is None:
            hours_ago = settings.ACCOUNT_DELETION_EXPUNGE_HOURS
        before = now() - datetime.timedelta(hours=hours_ago)
        count = 0
        for account_deletion in cls.objects.filter(date_requested__lt=before, user__isnull=False):
            settings.ACCOUNT_DELETION_EXPUNGE_CALLBACK(account_deletion)
            account_deletion.date_expunged = now()
            account_deletion.save()
            count += 1
        return count

    @classmethod
    def mark(cls, user):
        account_deletion, created = cls.objects.get_or_create(user=user)
        account_deletion.email = user.email
        account_deletion.save()
        settings.ACCOUNT_DELETION_MARK_CALLBACK(account_deletion)
        return account_deletion


class PasswordHistory(models.Model):
    """
    Contains single password history for user.
    """

    class Meta:
        verbose_name = _("Password History")
        verbose_name_plural = _("Password Histories")

    user = models.ForeignKey(to=Account, related_name="password_history", on_delete=models.CASCADE)
    password = models.CharField(max_length=255)  # encrypted password
    timestamp = models.DateTimeField(default=now)  # password creation time


class PasswordExpiry(models.Model):
    """
    Holds the password expiration period for a single user.
    """
    user = models.OneToOneField(to=Account, related_name="password_expiry", verbose_name=_("user"),
                                on_delete=models.CASCADE)
    expiry = models.PositiveIntegerField(default=0)


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


post_save.connect(user_post_save, sender=settings.AUTH_USER_MODEL)
post_save.connect(create_default_thumbnail, sender=Avatar)
if settings.AVATAR_CLEANUP_DELETED:
    post_delete.connect(remove_avatar_images, sender=Avatar)
