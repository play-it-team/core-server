#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

from enum import Enum


class ChoiceEnum(Enum):
	@classmethod
	def choices(cls):
		return tuple((i.name, i.value) for i in cls)


class AvatarSizeEnum(ChoiceEnum):
	avatar_128 = 128
	avatar_96 = 96
	avatar_64 = 64
	avatar_48 = 48
	avatar_32 = 32
	avatar_24 = 24
	avatar_16 = 16


class AccountGender(ChoiceEnum):
	M = 'Male'
	F = 'Female'
