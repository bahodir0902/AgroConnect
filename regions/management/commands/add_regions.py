from django.core.management.base import BaseCommand
from regions.models import Region


class Command(BaseCommand):
    help = 'Adds 13 administrative regions of Uzbekistan'

    def handle(self, *args, **kwargs):
        regions = [
            "Tashkent", "Samarkand", "Bukhara", "Khorezm", "Surkhandarya", "Kashkadarya", "Andijan",
            "Fergana", "Namangan", "Jizzakh", "Sirdaryo", "Navoi", "Karakalpakstan"
        ]

        created_count = 0
        for region_name in regions:
            region, created = Region.objects.get_or_create(name=region_name)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {region_name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Already exists: {region_name}"))

        self.stdout.write(
            self.style.SUCCESS(f"\nSuccessfully added {created_count} new regions out of {len(regions)} total")
        )
