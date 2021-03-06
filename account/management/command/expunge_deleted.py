#  Copyright (c) 2019 - 2020. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

from django.core.management.base import BaseCommand

from account.models import AccountDeletion


class Command(BaseCommand):
    help = "Expunge accounts deleted more than 48 hours ago."

    def handle(self, *args, **options):
        count = AccountDeletion.expunge()
        print("{0} expunged.".format(count))
