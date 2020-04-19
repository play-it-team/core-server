#  Copyright (c) 2019 - 2020. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors
import django.dispatch

avatar_updated = django.dispatch.Signal(providing_args=['account', 'avatar'])
avatar_deleted = django.dispatch.Signal(providing_args=['account', 'avatar'])
user_signed_up = django.dispatch.Signal(providing_args=["user", "form"])
user_sign_up_attempt = django.dispatch.Signal(providing_args=["username", "email", "result"])
user_logged_in = django.dispatch.Signal(providing_args=["user", "form"])
user_login_attempt = django.dispatch.Signal(providing_args=["username", "result"])
signup_code_sent = django.dispatch.Signal(providing_args=["signup_code"])
signup_code_used = django.dispatch.Signal(providing_args=["signup_code_result"])
email_confirmed = django.dispatch.Signal(providing_args=["email_address"])
email_confirmation_sent = django.dispatch.Signal(providing_args=["confirmation"])
password_changed = django.dispatch.Signal(providing_args=["user"])
password_expired = django.dispatch.Signal(providing_args=["user"])
