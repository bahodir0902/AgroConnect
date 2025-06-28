from rest_framework import serializers
from products.models import Product, PlantedProduct


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', "name", 'created_at', 'updated_at']
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True}
        }


class PlantedProductSerializer(serializers.ModelSerializer):
    # product = ProductSerializer(read_only=True)
    class Meta:
        model = PlantedProduct
        fields = ['id', "product", "owner", "region", "planting_area", "expecting_weight", "created_at", "updated_at"]
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "owner": {"required": True},
            "product": {"required": True},
            "region": {"required": True},
        }

class PlantedProductSerializerListAndRetrieve(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = PlantedProduct
        fields = ['id', "product", "owner", "region", "planting_area", "expecting_weight", "created_at", "updated_at"]
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "owner": {"required": True},
            "product": {"required": True},
            "region": {"required": True},
        }


