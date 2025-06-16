from django.contrib import admin
from regions.models import Region

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    pass