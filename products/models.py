from django.db import models
from accounts.models import User
from common.models import BaseModel
from regions.models import Region


class Product(BaseModel):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "Products"

    def __str__(self):
        return f"{self.name}"


class PlantedProduct(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='planted_products')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='planted_products')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='planted_products')
    planting_area = models.DecimalField(max_digits=15, decimal_places=3)
    expecting_weight = models.DecimalField(max_digits=15, decimal_places=3)

    class Meta:
        db_table = "Planted Products"

    def __str__(self):
        return f"Product name: {self.product.name}, Product owner: {self.owner.first_name}, Region: {self.region.name}"
