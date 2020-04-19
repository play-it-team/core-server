#  Copyright (c) 2019 - 2020. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

import binascii
import datetime
import functools
import hashlib
import logging
import os
from urllib.parse import urlparse, urlunparse

import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect, QueryDict
from django.urls import NoReverseMatch, reverse
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


def get_user_lookup_kwargs(kwargs):
    result = {}
    username_field = getattr(get_user_model(), "USERNAME_FIELD", "username")
    for key, value in kwargs.items():
        result[key.format(username=username_field)] = value
    return result


def default_redirect(request, fallback_url, **kwargs):
    redirect_field_name = kwargs.get("redirect_field_name", "next")
    next_url = request.POST.get(redirect_field_name, request.GET.get(redirect_field_name))
    if not next_url:
        # try the session if available
        if hasattr(request, "session"):
            session_key_value = kwargs.get("session_key_value", "redirect_to")
            if session_key_value in request.session:
                next_url = request.session[session_key_value]
                del request.session[session_key_value]
    is_safe = functools.partial(
        ensure_safe_url,
        allowed_protocols=kwargs.get("allowed_protocols"),
        allowed_host=request.get_host()
    )
    if next_url and is_safe(next_url):
        return next_url
    else:
        try:
            fallback_url = reverse(fallback_url)
        except NoReverseMatch:
            if callable(fallback_url):
                raise
            if "/" not in fallback_url and "." not in fallback_url:
                raise
        # assert the fallback URL is safe to return to caller. if it is
        # determined unsafe then raise an exception as the fallback value comes
        # from the a source the developer choose.
        is_safe(fallback_url, raise_on_fail=True)
        return fallback_url


def user_display(user):
    return settings.ACCOUNT_USER_DISPLAY(user)


def ensure_safe_url(url, allowed_protocols=None, allowed_host=None, raise_on_fail=False):
    if allowed_protocols is None:
        allowed_protocols = ["http", "https"]
    parsed = urlparse(url)
    # perform security checks to ensure no malicious intent
    # (i.e., an XSS attack with a data URL)
    safe = True
    if parsed.scheme and parsed.scheme not in allowed_protocols:
        if raise_on_fail:
            raise SuspiciousOperation("Unsafe redirect to URL with protocol '{0}'".format(parsed.scheme))
        safe = False
    if allowed_host and parsed.netloc and parsed.netloc != allowed_host:
        if raise_on_fail:
            raise SuspiciousOperation("Unsafe redirect to URL not matching host '{0}'".format(allowed_host))
        safe = False
    return safe


def handle_redirect_to_login(request, **kwargs):
    login_url = kwargs.get("login_url")
    redirect_field_name = kwargs.get("redirect_field_name")
    next_url = kwargs.get("next_url")
    if login_url is None:
        login_url = settings.ACCOUNT_LOGIN_URL
    if next_url is None:
        next_url = request.get_full_path()
    try:
        login_url = reverse(login_url)
    except NoReverseMatch:
        if callable(login_url):
            raise
        if "/" not in login_url and "." not in login_url:
            raise
    url_bits = list(urlparse(login_url))
    if redirect_field_name:
        querystring = QueryDict(url_bits[4], mutable=True)
        querystring[redirect_field_name] = next_url
        url_bits[4] = querystring.urlencode(safe="/")
    return HttpResponseRedirect(urlunparse(url_bits))


def get_form_data(form, field_name, default=None):
    if form.prefix:
        key = "-".join([form.prefix, field_name])
    else:
        key = field_name
    return form.data.get(key, default)


def check_password_expired(user):
    """
    Return True if password is expired and system is using
    password expiration, False otherwise.
    """
    if not settings.ACCOUNT_PASSWORD_USE_HISTORY:
        return False

    if hasattr(user, "password_expiry"):
        # user-specific value
        expiry = user.password_expiry.expiry
    else:
        # use global value
        expiry = settings.ACCOUNT_PASSWORD_EXPIRY

    if expiry == 0:  # zero indicates no expiration
        return False

    try:
        # get latest password info
        latest = user.password_history.latest("timestamp")
    except:
        return False

    now = datetime.datetime.now(tz=pytz.UTC)
    expiration = latest.timestamp + datetime.timedelta(seconds=expiry)

    if expiration < now:
        return True
    else:
        return False
