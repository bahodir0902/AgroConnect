from rest_framework import serializers

from products.models import PlantedProduct
from regions.models import Region


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', "name", "country", "created_at", "updated_at"]
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True}
        }


# class WPHPerRegionSerializer(serializers.ModelSerializer):
#     wph = serializers.SerializerMethodField()
#     class Meta:
#         model = PlantedProduct
#         fields = ['id', "expecting_weight", 'planting_area', 'region', 'product', 'wph']
#         extra_kwargs = {
#             "id": {"read_only": True},
#         }
#
#     def get_wph(self, obj: PlantedProduct):
#         return float(obj.expecting_weight / obj.planting_area)

# class WPHForAllRegions(serializers.ModelSerializer):
#     wph = serializers.SerializerMethodField()
#     class Meta:
#         model = PlantedProduct
#         fields = ['id', "expecting_weight", 'planting_area', 'region', 'product', 'wph']
#         extra_kwargs = {
#             "id": {"read_only": True},
#         }
#     def get_wph(self, obj: PlantedProduct):
#         pass