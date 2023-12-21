import os

from django.core.management.base import BaseCommand, CommandError

from test.bot import main


class Command(BaseCommand):
    help = "Run telegram bot"

    def handle(self, *args, **options):
        main()