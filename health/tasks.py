#  Copyright (c) 2019 - 2019. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

from celery import shared_task


@shared_task(ignore_result=False)
def add(x, y):
	return x + y
