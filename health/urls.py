#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

from django.urls import include, re_path

from health.api.base.routers import api_urlpatterns as api_v1

app_name = 'health'

urlpatterns = [
		re_path(r'^v1/', include(api_v1)),
]
