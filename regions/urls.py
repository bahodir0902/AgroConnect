from django.urls import path
from regions.views import RegionAPIView

app_name = "regions"
urlpatterns = [
    path("", RegionAPIView.as_view(), name="regions")
]
