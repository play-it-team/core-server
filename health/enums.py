#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors
from enum import Enum


class ChoiceEnum(Enum):
	@classmethod
	def choices(cls):
		return tuple((i.name, i.value) for i in cls)


class HealthStatusEnum(ChoiceEnum):
	green = 0
	yellow = 1
	orange = 2
	red = 3
