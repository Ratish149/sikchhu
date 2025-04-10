from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    ForgotPasswordConfirmView, ForgotPasswordView, RegisterView, LoginView, ResendVerificationEmailView, VerifyEmailView,
    UserProfileView, UserListView,
    ChangePasswordView, OrganizationListCreateView,
    OrganizationDetailView
)

urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', LoginView.as_view(), name='login'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('resend-verification-email/', ResendVerificationEmailView.as_view(),
         name='resend-verification-email'),

    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('forgot-password-confirm/', ForgotPasswordConfirmView.as_view(),
         name='forgot-password-confirm'),

    path('profile/', UserProfileView.as_view(), name='profile'),
    path('users/', UserListView.as_view(), name='users'),
    path('organizations/', OrganizationListCreateView.as_view(), name='organizations'),
    path('organizations/<int:pk>/', OrganizationDetailView.as_view(),
         name='organization-detail'),
]
