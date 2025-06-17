from django.contrib import admin
from products.models import Product, PlantedProduct

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(PlantedProduct)
class PlantedProductAdmin(admin.ModelAdmin):
    pass