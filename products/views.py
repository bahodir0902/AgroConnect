from accounts.utils import log_activity
from products.models import Product, PlantedProduct
from products.serializers import ProductSerializer, PlantedProductSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from accounts.permissions import IsAdminUser


class ProductModelViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action in ['create', 'update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class PlantedProductModelViewSet(ModelViewSet):
    serializer_class = PlantedProductSerializer
    queryset = PlantedProduct.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()
        log_activity(instance.owner, "CREATE", instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(instance.owner, "UPDATE", instance)

    def perform_destroy(self, instance):
        log_activity(instance.owner, "DELETE", instance)
