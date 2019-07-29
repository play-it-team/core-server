#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

from django.urls import include, path
from rest_framework import routers

from health import views

app_name = 'health'

router = routers.DefaultRouter()
router.register(r'services', views.ServiceViewSet)

urlpatterns = [
		path('', include(router.urls)),
]
