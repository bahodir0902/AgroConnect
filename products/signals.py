from django.db.models.signals import post_save
from django.dispatch import receiver
from products.models import Product
from products.service import translate_product_name

@receiver(post_save, sender=Product)
def auto_translate_name(sender, instance, created, **kwargs):
    if created:
        translate_product_name(instance)
