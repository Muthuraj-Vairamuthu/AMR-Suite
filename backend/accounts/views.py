# AMR-Suite/backend/accounts/views.py
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialLogin, SocialAccount
from .serializers import RegisterSerializer, LoginSerializer, CustomUserSerializer  # Add this import
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetOTP, CustomUser
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegistrationForm, UserLoginForm

class RegisterView(View):
    template_name = 'signup_page.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('upload_dataset')
        return render(request, self.template_name)
    
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('upload_dataset')
        messages.error(request, 'Registration failed')
        return render(request, self.template_name)

class LoginView(View):
    template_name = 'login_page.html'

    def get(self, request):
        context = {
            'social_auth_enabled': True  # Since we have social auth configured
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('upload_dataset')
        messages.error(request, 'Invalid credentials')
        return render(request, self.template_name, {'social_auth_enabled': True})

class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('accounts:login')

class GoogleLoginView(APIView):
    def post(self, request):
        adapter = GoogleOAuth2Adapter(request)
        client = OAuth2Client(request)
        token = client.get_access_token(request.data['code'])
        login_data = adapter.complete_login(request, token)
        social_login = SocialLogin(login=login_data)
        user = social_login.connect(request)
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
        
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get the current user's profile."""
        try:
            serializer = CustomUserSerializer(request.user)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": "Failed to retrieve user profile", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request):
        """Update the current user's profile."""
        try:
            # Only allow updating specific fields
            allowed_fields = {'first_name', 'last_name', 'profile_picture'}
            data = {k: v for k, v in request.data.items() if k in allowed_fields}

            serializer = CustomUserSerializer(request.user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Failed to update user profile", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RequestPasswordResetOTPView(APIView):
    def post(self, request):
        """Generate and send OTP for password reset."""
        email = request.data.get('email')
        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(email=email)
            otp_obj = PasswordResetOTP.generate_otp(user)

            # Send email with OTP
            subject = "Password Reset OTP for AMR-Suite"
            message = f"""
Hello {user.first_name},

You've requested to reset your password for your AMR-Suite account.

Your OTP is: {otp_obj.otp}

This OTP is valid for 10 minutes. If you didn't request this, please ignore this email.

Thanks,
The AMR-Suite Team
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            return Response(
                {"detail": "Password reset OTP has been sent to your email."},
                status=status.HTTP_200_OK
            )
        except CustomUser.DoesNotExist:
            # Don't reveal that the user doesn't exist for security reasons
            return Response(
                {"detail": "If a user with this email exists, an OTP has been sent."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "Failed to send OTP", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
# AMR-Suite/backend/accounts/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import PasswordResetOTP, CustomUser

class VerifyOTPAndResetPasswordView(APIView):
    def post(self, request):
        """Verify OTP and reset password."""
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not all([email, otp, new_password]):
            return Response(
                {"error": "Email, OTP, and new password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(email=email)
            otp_obj = PasswordResetOTP.objects.filter(
                user=user, 
                otp=otp, 
                is_used=False
            ).latest('created_at')

            if not otp_obj.is_valid():
                return Response(
                    {"error": "OTP has expired. Please request a new one."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Reset password
            user.set_password(new_password)
            user.save()

            # Mark OTP as used
            otp_obj.is_used = True
            otp_obj.save()

            return Response(
                {"detail": "Password has been reset successfully."},
                status=status.HTTP_200_OK
            )
        except PasswordResetOTP.DoesNotExist:
            return Response(
                {"error": "Invalid OTP. Please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User with this email doesn't exist."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "Failed to reset password", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
# AMR-Suite/backend/accounts/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Change the current user's password."""
        old_password = request.data.get('old_password')
        new_password1 = request.data.get('new_password1')
        new_password2 = request.data.get('new_password2')

        if not all([old_password, new_password1, new_password2]):
            return Response(
                {"error": "All password fields are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_password1 != new_password2:
            return Response(
                {"error": "New passwords don't match."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user

        # Check if the old password is correct
        if not user.check_password(old_password):
            return Response(
                {"error": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set the new password
        user.set_password(new_password1)
        user.save()

        # Update the session after password change
        update_session_auth_hash(request, user)

        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK
        )