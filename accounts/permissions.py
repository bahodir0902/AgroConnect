from django.contrib.auth.models import Group
from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        admin_group, _ = Group.objects.get_or_create(name='Admins')
        if user.is_superuser or user.is_staff or user.groups.all().first() == admin_group:
            return True
        return bool(
            user and user.is_authenticated
            and (user.is_staff or user.is_superuser)
        )