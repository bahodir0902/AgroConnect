import random
from .models import RecentActivity

def generate_random_code():
    return random.randint(1000, 9999)


def log_activity(user, action, instance):
    """
    Log user activity for model instances
    Args:
        user: User instance
        action: 'CREATE', 'UPDATE', or 'DELETE'
        instance: Model instance (Product, PlantedProduct, Region)
    """
    model_name = instance._meta.model_name.title()
    if model_name == 'Plantedproduct':
        model_name = 'PlantedProduct'

    recent_count = RecentActivity.objects.filter(user=user).count()
    if recent_count >= 500:
        oldest_activities = RecentActivity.objects.filter(user=user).order_by('timestamp')[:10]
        RecentActivity.objects.filter(
            id__in=[activity.id for activity in oldest_activities]
        ).delete()

    RecentActivity.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=instance.id,
        object_name=str(instance)
    )
