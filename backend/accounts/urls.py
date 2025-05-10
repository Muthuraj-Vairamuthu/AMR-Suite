# AMR-Suite/backend/accounts/urls.py
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import views as auth_views
from .views import (
    RegisterView,
    LoginView,
    GoogleLoginView,
    UserProfileView,
    RequestPasswordResetOTPView,
    VerifyOTPAndResetPasswordView,
    ChangePasswordView,
    LogoutView,
)

app_name = 'accounts'

urlpatterns = [
    # User registration and login
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Google OAuth
    path('google/login/', GoogleLoginView.as_view(), name='google-login'),

    # User profile
    path('profile/', UserProfileView.as_view(), name='profile'),

    # Password reset endpoints
    path('password/reset/', 
        auth_views.PasswordResetView.as_view(
            html_email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
            template_name='registration/password_reset_form.html'
        ), 
        name='password_reset'
    ),
    path('password/reset/done/', 
        auth_views.PasswordResetDoneView.as_view(), 
        name='password_reset_done'
    ),
    path('password/reset/confirm/<uidb64>/<token>/',  
        auth_views.PasswordResetConfirmView.as_view(
            success_url='/accounts/password/reset/complete/'
        ), 
        name='password_reset_confirm'
    ),
    path('password/reset/complete/', 
        auth_views.PasswordResetCompleteView.as_view(), 
        name='password_reset_complete'
    ),

    # OTP-based Password Reset
    path('password/reset-otp/', 
        RequestPasswordResetOTPView.as_view(), 
        name='reset-otp'
    ),
    path('password/reset-verify/', 
        VerifyOTPAndResetPasswordView.as_view(), 
        name='reset-verify'
    ),

    # Password change for authenticated users
    path('password/change/',
        ChangePasswordView.as_view(),
        name='change-password'
    ),
    
    # Include allauth URLs
    path('', include('allauth.urls')),
]