from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Add 100 harvesting products to the database'

    def handle(self, *args, **options):
        products = [
            # Fruits
            "Apple", "Orange", "Banana", "Grape", "Strawberry", "Blueberry", "Raspberry", "Blackberry",
            "Peach", "Pear", "Plum", "Cherry", "Apricot", "Mango", "Pineapple", "Watermelon",
            "Cantaloupe", "Honeydew", "Kiwi", "Papaya", "Avocado", "Coconut", "Pomegranate", "Fig",
            "Date", "Cranberry", "Gooseberry", "Elderberry", "Currant", "Lemon", "Lime", "Grapefruit",

            # Vegetables
            "Potato", "Tomato", "Carrot", "Onion", "Garlic", "Broccoli", "Cauliflower", "Cabbage",
            "Lettuce", "Spinach", "Kale", "Cucumber", "Zucchini", "Squash", "Pumpkin", "Bell Pepper",
            "Hot Pepper", "Eggplant", "Radish", "Turnip", "Beet", "Sweet Potato", "Corn", "Green Bean",
            "Pea", "Lima Bean", "Okra", "Asparagus", "Artichoke", "Brussels Sprout", "Celery", "Parsnip",

            # Grains & Cereals
            "Wheat", "Rice", "Corn", "Barley", "Oats", "Rye", "Quinoa", "Buckwheat", "Millet", "Sorghum",

            # Legumes
            "Soybean", "Black Bean", "Kidney Bean", "Navy Bean", "Pinto Bean", "Chickpea", "Lentil", "Black-eyed Pea",

            # Nuts & Seeds
            "Almond", "Walnut", "Pecan", "Hazelnut", "Cashew", "Pistachio", "Macadamia", "Sunflower Seed",
            "Pumpkin Seed", "Flax Seed", "Chia Seed", "Sesame Seed",

            # Herbs & Spices
            "Basil", "Oregano", "Thyme", "Rosemary", "Sage", "Parsley", "Cilantro", "Dill",
            "Mint", "Chives", "Tarragon", "Lavender",

            # Root Vegetables
            "Ginger", "Turmeric", "Horseradish", "Rutabaga", "Jicama", "Yam",

            # Specialty Crops
            "Cotton", "Tobacco", "Sugar Beet", "Sugar Cane", "Tea Leaf", "Coffee Bean", "Vanilla Bean", "Hops"
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