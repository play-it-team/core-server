#  Copyright (c) 2019 - 2020. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

import pytz
from django.db import models


class TimeZoneField(models.CharField):

    def __init__(self, *args, **kwargs):
        defaults = {
            "max_length": 100,
            "default": "",
            "choices": tuple((t, t) for t in pytz.all_timezones),
            "blank": True,
        }
        defaults.update(kwargs)
        return super(TimeZoneField, self).__init__(*args, **defaults)
