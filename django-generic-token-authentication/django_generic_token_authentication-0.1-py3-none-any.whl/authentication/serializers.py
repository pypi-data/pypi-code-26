from django.conf import settings

from rest_framework import serializers

from authentication.models import User


class RegisterSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False, read_only=True)
    username = serializers.CharField(max_length=50, required=True)
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ('id', 'password', 'username', 'email', 'first_name', 'last_name')


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False, read_only=True)
    username = serializers.CharField(max_length=50, required=True)
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class RefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=settings.REFRESH_TOKEN_LENGTH, required=True)