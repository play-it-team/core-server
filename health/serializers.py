#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors
from rest_framework import serializers

from health.models import Service


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Service
		fields = ['name', 'slug', 'description', 'status', 'order', 'created_on', 'updated_on']
