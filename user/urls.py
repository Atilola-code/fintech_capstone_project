from django.urls import path
from .views import RegisterUsers, LoginUsers, KYCUploadView, CurrentUserView, AdminUserListView, VerifyEmailOTPView, ResendEmailOTPView

urlpatterns = [
    path('register/', RegisterUsers.as_view(), name="register"),
    path('verify-email-otp/', VerifyEmailOTPView.as_view(), name='verify-email-otp'),
    path('resend-email-otp/', ResendEmailOTPView.as_view(), name='resend-email-otp'),
    path('login/', LoginUsers.as_view(), name="login"),
    path('kyc/upload/', KYCUploadView.as_view(), name='kyc_upload'),
    path('single-user/', CurrentUserView.as_view(), name='current-user'),
    path('all-users/', AdminUserListView.as_view(), name='admin-user-list'),
]