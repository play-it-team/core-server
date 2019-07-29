#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors
from rest_framework import routers

from health.api.base.views import ServiceViewSet

router = routers.DefaultRouter()
router.register(r'services', ServiceViewSet)

api_urlpatterns = router.urls
