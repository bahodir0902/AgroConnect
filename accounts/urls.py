from django.urls import path
from accounts.views import (
    RegisterView,
    CustomTokenObtainPairView,
    LogoutView,
    UserProfileView,
    CustomTokenRefreshView
)

app_name = "accounts"
urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', CustomTokenObtainPairView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('profile/', UserProfileView.as_view(), name="profile"),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name="token_refresh"),
]