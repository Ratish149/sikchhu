from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomToken(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['phone_number'] = user.phone_number
        token['user_type'] = user.user_type
        token['is_verified'] = user.is_verified
        token['profile_picture'] = user.profile_picture.url if user.profile_picture else None
        token['organization'] = user.organization.id if user.organization else None

        return token
