#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors
import django.dispatch

avatar_updated = django.dispatch.Signal(providing_args=['account', 'avatar'])
avatar_deleted = django.dispatch.Signal(providing_args=['account', 'avatar'])
