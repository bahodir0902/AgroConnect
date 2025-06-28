from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Add 100 harvesting products to the database'

    def handle(self, *args, **options):
        products = [
            # Fruits - Mevalar
            "Olma", "Apelsin", "Banan", "Uzum", "Qulupnay", "Ko'k rezavor", "Qizil rezavor", "Qora rezavor",
            "Shaftoli", "Nok", "Olxo'ri", "Olcha", "O'rik", "Mango", "Ananas", "Tarvuz",
            "Qovun", "Asal qovuni", "Kivi", "Papaya", "Avokado", "Hindiston yong'og'i", "Anor", "Anjir",
            "Xurmo", "Kızılcık", "Chuqur rezavor", "Rovashan", "Smorodina", "Limon", "Laym", "Greypfrut",

            # Vegetables - Sabzavotlar
            "Kartoshka", "Pomidor", "Sabzi", "Piyoz", "Sarimsoq", "Brokkoli", "Gulkaram", "Karam",
            "Salat bargi", "Ismaloq", "Karam bargi", "Bodring", "Qovoq", "Qovoq", "Oshqovoq", "Bulgari qalampiri",
            "Achchiq qalampir", "Baqlajon", "Turp", "Sholg'om", "Lavlagi", "Shirin kartoshka", "Makkajo'xori", "Yashil loviya",
            "No'xat", "Lima loviyasi", "Bamiya", "Qushqo'nmasi", "Artishok", "Brussel karami", "Kraxmal", "Parsnip",

            # Grains & Cereals - Don va donli ekinlar
            "Bug'doy", "Guruch", "Makkajo'xori", "Arpa", "Jo", "Javdar", "Kinoa", "Qora bug'doy", "Tariq", "Sorghum",

            # Legumes - Dukkakli o'simliklar
            "Soya loviyasi", "Qora loviya", "Buyrak loviyasi", "Oq loviya", "Pinto loviyasi", "No'xat", "Yasmiq", "Qora ko'zli no'xat",

            # Nuts & Seeds - Yong'oq va urug'lar
            "Bodom", "Yong'oq", "Pekan", "Findiq", "Kaju", "Pista", "Makademiya", "Kungaboqar urgi",
            "Qovoq urgi", "Zig'ir urgi", "Chia urgi", "Kunjut urgi",

            # Herbs & Spices - O'tlar va ziravorlar
            "Reyhan", "Oregano", "Kekik", "Rozmarin", "Adaçayı", "Jafari", "Kashnich", "Archa",
            "Yalpiz", "Piyozcha", "Tarhun", "Lavanda",

            # Root Vegetables - Ildiz sabzavotlar
            "Zanjabil", "Zerdeçal", "Xantal", "Rutabaga", "Jikama", "Qand kartoshkasi",

            # Specialty Crops - Maxsus ekinlar
            "Paxta", "Tamaki", "Qand lavlagi", "Qand qamishi", "Choy bargi", "Qahva loviyasi", "Vanil loviyasi", "Hop"
        ]

        created_count = 0
        for product_name in products:
            product, created = Product.objects.get_or_create(name=product_name)
            if created:
                created_count += 1
                self.stdout.write(f"Created: {product_name}")
            else:
                self.stdout.write(f"Already exists: {product_name}")

        self.stdout.write(
            self.style.SUCCESS(f'Successfully added {created_count} new products out of {len(products)} total products')
        )