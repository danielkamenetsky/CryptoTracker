from django.core.management.base import BaseCommand
from price_updater.service import main

class Command(BaseCommand):
    help = 'Fetches cryptocurrency prices and sends them to Kafka'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting price updater service...'))
        main()
