#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

from enum import Enum


class ChoiceEnum(Enum):
	@classmethod
	def choices(cls):
		return tuple((i.name, i.value) for i in cls)


class ContinentEnum(ChoiceEnum):
	AF = 'Africa'
	AS = 'Asia'
	EU = 'Europe'
	NA = 'North America'
	OC = 'Oceania'
	SA = 'South America'
	AN = 'Antartica'
