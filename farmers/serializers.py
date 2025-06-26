from rest_framework import serializers
from accounts.models import User
from products.models import Product, PlantedProduct
from products.serializers import ProductSerializer


# class ProductSerializerForFarmer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = ['id', 'name']
#         extra_kwargs = {
#             "id": {"read_only": True}
#         }
#

class PlantedProductForFarmerSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    wph = serializers.SerializerMethodField()

    class Meta:
        model = PlantedProduct
        fields = ['product', 'planting_area', 'expecting_weight', 'wph', 'created_at', 'updated_at']

    def get_wph(self, obj):
        return obj.expecting_weight / obj.planting_area


class FarmerSerializer(serializers.ModelSerializer):
    planted_products = PlantedProductForFarmerSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'region', 'planted_products')
