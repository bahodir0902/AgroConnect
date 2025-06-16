from django.urls import path
from products.views import ProductModelViewSet, PlantedProductModelViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("products", ProductModelViewSet, basename="products")
router.register("planted-products", PlantedProductModelViewSet, basename="planted_products")

app_name = "products"
urlpatterns = router.urls
