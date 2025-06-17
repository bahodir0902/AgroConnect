from django.urls import path
from products.views import ProductModelViewSet, PlantedProductModelViewSet, WPHPerRegion, WPHPerRegionPerProduct, \
    WPHComparison, WPHMatrix
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("products", ProductModelViewSet, basename="products")
router.register("planted-products", PlantedProductModelViewSet, basename="planted_products")

app_name = "products"
urlpatterns = [
    path("WPHPerRegion/", WPHPerRegion.as_view(), name="WPHPerRegion"),
    path('wph/region/', WPHPerRegion.as_view(), name='wph-per-region'),
    path('wph/region-product/', WPHPerRegionPerProduct.as_view(), name='wph-per-region-per-product'),
    path('wph/comparison/', WPHComparison.as_view(), name='wph-comparison'),
    path('wph/matrix/', WPHMatrix.as_view(), name='wph-matrix'),
]  + router.urls

