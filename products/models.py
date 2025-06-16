from django.db import models
from accounts.models import User
from common.models import BaseModel

# class Product(BaseModel):
#     name = models.CharField(max_length=255)
#     area = models.DecimalField(decimal_places=3, max_digits=15)
#     owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
#
#
#     class Meta:
#         db_table = "Products"
