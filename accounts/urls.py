from django.urls import path
from accounts.views import *

app_name = "accounts"
urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', CustomTokenObtainPairView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('profile/', UserProfileView.as_view(), name="profile"),
    path('profile/request-email-change/', RequestEmailChange.as_view(), name="request_email_change"),
    path('profile/confirm-email-change/', ConfirmEmailChange.as_view(), name="confirm_email_change"),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name="token_refresh"),
    path('delete/', DeleteAccountView.as_view(), name="delete_account"),
    path('password-reset/request/', ForgotPasswordView.as_view(), name='password_reset_request'),
    path('password-reset/verify/', VerifyPasswordResetView.as_view(), name='password_reset_verify'),
    path('password-reset/confirm/', ResetPasswordView.as_view(), name='password_reset_confirm'),
    path('verify-register/', VerifyRegistration.as_view(), name='verify_registration'),
    path('login/google/', GoogleLoginView.as_view(), name='google_login'),
    path('login/google/callback/', GoogleCallBackView.as_view(), name='google_callback'),
    path('login/google/complete-profile/', CompleteGoogleRegistration.as_view(), name='complete_google_registration'),
    path('recent-activities/', RecentActivities.as_view(), name="recent_activities"),
]
