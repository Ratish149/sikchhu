from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .models import CustomUser
from .serializers import LoginSerializer, UserSerializer

# Create your views here.


class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Get all data directly from the request
            email = request.data.get('email')
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            phone_number = request.data.get('phone_number', None)
            user_type = request.data.get('user_type', 'Student')
            password = request.data.get('password')
            profile_picture = request.FILES.get('profile_picture', None)

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
                password=make_password(password)  # Hash the password
            )

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
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

            user = None

            # Try to authenticate with email
            try:
                user_obj = CustomUser.objects.get(email=email)
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
