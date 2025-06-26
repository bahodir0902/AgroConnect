from django.urls import path
from farmers.views import FarmerAPIView

urlpatterns = [
    path('', FarmerAPIView.as_view(), name='farmer-list'),
]
