from django.db import models
from common.models import BaseModel


class Region(BaseModel):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255, default="Uzbekistan")

    class Meta:
        db_table = "Regions"

    def __str__(self):
        return f"{self.name} - {self.country}"
