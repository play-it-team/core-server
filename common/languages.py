#  Copyright (c) 2019 - 2020. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

from django.conf import settings
from django.utils.translation import get_language_info

"""
# List of language code and languages local names.
#
# This list is output of code:

[
    (code, get_language_info(code).get("name_local"))
    for code, lang in settings.LANGUAGES
]
"""

DEFAULT_LANGUAGE = get_language_info(settings.LANGUAGE_CODE)["code"]
