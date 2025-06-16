from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from accounts.models import RecentActivity
from products.models import Product, PlantedProduct
from regions.models import Region
from accounts.utils import log_activity

User = get_user_model()

@receiver(post_save, sender=User)
def assign_default_group(sender, instance, created, **kwargs):
    if created and not instance.groups.exists():
        users_group, _ = Group.objects.get_or_create(name="Users")
        instance.groups.add(users_group)

@receiver(post_save, sender=Product)
def log_product_activity(sender, instance, created, **kwargs):
    if hasattr(instance, '_current_user') and instance._current_user:
        action = 'CREATE' if created else 'UPDATE'
        log_activity(instance._current_user, action, instance)

@receiver(post_save, sender=Region)
def log_region_activity(sender, instance, created, **kwargs):
    if hasattr(instance, '_current_user') and instance._current_user:
        action = 'CREATE' if created else 'UPDATE'
        log_activity(instance._current_user, action, instance)

@receiver(post_delete, sender=Product)
def log_product_deletion(sender, instance, **kwargs):
    if hasattr(instance, '_current_user') and instance._current_user:
        log_activity(instance._current_user, 'DELETE', instance)


@receiver(post_delete, sender=Region)
def log_region_deletion(sender, instance, **kwargs):
    if hasattr(instance, '_current_user') and instance._current_user:
        log_activity(instance._current_user, 'DELETE', instance)
#
# @receiver(post_save, sender=PlantedProduct)
# def log_planted_product_activity(sender, instance, created, **kwargs):
#     if instance.owner:  # PlantedProduct has owner field
#         action = 'CREATE' if created else 'UPDATE'
#         log_activity(instance.owner, action, instance)
#
# @receiver(post_delete, sender=PlantedProduct)
# def log_planted_product_deletion(sender, instance, **kwargs):
#     if instance.owner:
#         log_activity(instance.owner, 'DELETE', instance)
