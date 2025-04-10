from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .models import CustomUser, Organization
from .serializers import ChangePasswordSerializer, LoginSerializer, UserSerializer, OrganizationSerializer, VerifyEmailSerializer
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import random
from datetime import datetime, timedelta
import time
import base64
import hmac
import hashlib

# Create your views here.


class OrganizationListCreateView(generics.ListCreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def send_verification_email(self, user, token):
        subject = 'Email Verification - Sikchhu'
        context = {
            'user': user,
            'token': token,
            'frontend_url': 'http://localhost:3000'
        }
        html_message = render_to_string('email_verification.html', context)
        plain_message = strip_tags(html_message)

        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email: {str(e)}")

    def create(self, request, *args, **kwargs):
        try:
            # Get all data directly from the request
            email = request.data.get('email')
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            phone_number = request.data.get('phone_number', None)
            user_type = request.data.get('user_type', 'user')
            password = request.data.get('password')
            profile_picture = request.FILES.get('profile_picture', None)
            organization_id = request.data.get('organization_id', None)

            # Validate required fields
            if not email:
                return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not password:
                return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Extract username from email (part before @)
            username = email.split('@')[0]

            # Check if email already exists
            if CustomUser.objects.filter(email=email).exists():
                return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if phone_number and CustomUser.objects.filter(phone_number=phone_number).exists():
                return Response({'error': 'Phone number already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Create new user with optional fields handled properly
            user = CustomUser.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                user_type=user_type,
                profile_picture=profile_picture,
                password=make_password(password),
                organization_id=organization_id,
                is_verified=False
            )

            # Generate verification token
            token = encode_user_id(user.id)

            # Send verification email
            self.send_verification_email(user, token)

            # Build the profile picture URL only if it exists
            profile_picture_url = None
            if user.profile_picture and hasattr(user.profile_picture, 'url'):
                profile_picture_url = request.build_absolute_uri(
                    user.profile_picture.url)

            # Return user data and tokens
            return Response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': user.phone_number,
                    'user_type': user.user_type,
                    'profile_picture': profile_picture_url,
                    'is_verified': user.is_verified
                },
                'message': 'Registration successful. Please check your email for verification link.'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def encode_user_id(user_id):
    """Encode user ID with timestamp to create activation token"""
    timestamp = str(int(time.time()))
    message = f"{user_id}:{timestamp}"
    # Create a hash using user_id, timestamp, and secret key
    signature = hashlib.sha256(
        f"{message}:{settings.SECRET_KEY}".encode()).hexdigest()[:8]
    # Combine all parts
    token = f"{message}:{signature}"
    # Convert to base64 to make it URL-safe
    return base64.urlsafe_b64encode(token.encode()).decode()


def decode_user_id(token, max_age=72*3600):  # 72 hours expiry
    try:
        # Decode base64
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        # Split parts
        user_id_str, timestamp_str, signature = decoded.rsplit(':', 2)
        # Verify signature
        message = f"{user_id_str}:{timestamp_str}"
        expected_signature = hashlib.sha256(
            f"{message}:{settings.SECRET_KEY}".encode()).hexdigest()[:8]
        if not hmac.compare_digest(signature, expected_signature):
            return None

        # Check timestamp
        timestamp = int(timestamp_str)
        if time.time() - timestamp > max_age:
            return None

        return int(user_id_str)
    except Exception:
        return None


class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        try:
            # Get credentials from request - only email is required now
            email = request.data.get('email')
            password = request.data.get('password')

            if not email:
                return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not password:
                return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Try to authenticate with email
            try:
                user_obj = CustomUser.objects.get(email=email)
                if not user_obj.is_verified:
                    return Response({'error': 'Email not verified'}, status=status.HTTP_401_UNAUTHORIZED)

                user = authenticate(
                    username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass

            if not user:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            # Build the profile picture URL only if it exists
            profile_picture_url = None
            if user.profile_picture and hasattr(user.profile_picture, 'url'):
                profile_picture_url = request.build_absolute_uri(
                    user.profile_picture.url)

            # Return user data and tokens
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': user.phone_number,
                    'user_type': user.user_type,
                    'profile_picture': profile_picture_url
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = CustomUser.objects.all()

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        try:
            user = self.get_object()

            # Build the profile picture URL only if it exists
            profile_picture_url = None
            if user.profile_picture and hasattr(user.profile_picture, 'url'):
                profile_picture_url = request.build_absolute_uri(
                    user.profile_picture.url)

            # Return user data
            return Response({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
                'user_type': user.user_type,
                'profile_picture': profile_picture_url
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            user = self.get_object()

            # Get all data directly from the request - all fields are optional for updates
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            email = request.data.get('email')
            phone_number = request.data.get('phone_number')
            user_type = request.data.get('user_type')
            profile_picture = request.FILES.get('profile_picture')

            # Handle setting null values for nullable fields if explicitly provided
            if 'phone_number' in request.data and phone_number == '':
                phone_number = None
                user.phone_number = None

            # Update user fields if provided (not None)
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if email is not None and email != '':
                # Check if email is already taken by another user
                if email != user.email and CustomUser.objects.exclude(id=user.id).filter(email=email).exists():
                    return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

                # Update username if email changes
                if email != user.email:
                    username = email.split('@')[0]
                    base_username = username
                    count = 1
                    while CustomUser.objects.exclude(id=user.id).filter(username=username).exists():
                        username = f"{base_username}{count}"
                        count += 1
                    user.username = username

                user.email = email

            if phone_number is not None:
                # Check if phone is already taken by another user
                if phone_number != user.phone_number and CustomUser.objects.exclude(id=user.id).filter(phone_number=phone_number).exists():
                    return Response({'error': 'Phone number already exists'}, status=status.HTTP_400_BAD_REQUEST)
                user.phone_number = phone_number
            if user_type is not None:
                user.user_type = user_type
            if profile_picture is not None:
                user.profile_picture = profile_picture
            elif 'profile_picture' in request.data and not profile_picture:
                # Handle removing profile picture if empty value provided
                user.profile_picture = None

            user.save()

            # Build the profile picture URL only if it exists
            profile_picture_url = None
            if user.profile_picture and hasattr(user.profile_picture, 'url'):
                profile_picture_url = request.build_absolute_uri(
                    user.profile_picture.url)

            # Return updated user data
            return Response({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
                'user_type': user.user_type,
                'profile_picture': profile_picture_url
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        try:
            users = self.get_queryset()
            data = []

            for user in users:
                # Build the profile picture URL only if it exists
                profile_picture_url = None
                if user.profile_picture and hasattr(user.profile_picture, 'url'):
                    profile_picture_url = request.build_absolute_uri(
                        user.profile_picture.url)

                data.append({
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': user.phone_number,
                    'user_type': user.user_type,
                    'profile_picture': profile_picture_url
                })

            return Response(data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.validated_data['new_password'] == serializer.validated_data['old_password']:
            return Response({'error': 'New password cannot be the same as the old password'}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.validated_data['new_password'] != serializer.validated_data['confirm_password']:
            return Response({'error': 'New password and confirm password do not match'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)


class VerifyEmailView(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            token = request.data.get('token')

            if not token:
                return Response(
                    {'error': 'Token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_id = decode_user_id(token)
            if not user_id:
                return Response(
                    {'error': 'Invalid or expired token'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if user.is_verified:
                return Response(
                    {'message': 'Email already verified'},
                    status=status.HTTP_200_OK
                )

            user.is_verified = True
            user.save()

            return Response(
                {
                    'message': 'Email verified successfully'
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ResendOTPView(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            email = request.data.get('email')

            if not email:
                return Response(
                    {'error': 'Email is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if user.is_verified:
                return Response(
                    {'error': 'Email is already verified'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate new OTP
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            user.otp = otp
            user.otp_created_at = datetime.now()
            user.save()

            # Send new verification email
            subject = 'Email Verification - New OTP'
            context = {
                'user': user,
                'otp_code': otp
            }
            html_message = render_to_string('email_verification.html', context)
            plain_message = strip_tags(html_message)

            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )

            return Response(
                {'message': 'New OTP has been sent to your email'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
