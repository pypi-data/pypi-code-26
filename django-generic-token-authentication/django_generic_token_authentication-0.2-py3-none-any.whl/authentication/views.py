import logging

from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out

from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from utility.functions import get_current_datetime
from utility.logger import get_log_msg

from generic.views import GenericViewset
from generic.factories import generic_factory
from generic.repositories import GenericRepository
from generic.validators import validate_many, is_value_unique
from generic.services import (generic_retrieve_single_service,
                              generic_retrieve_all_service,
                              generic_delete_service,
                              generic_update_service,
                              generic_create_service)

from authentication.models import User
from authentication.serializers import UserSerializer, RegisterSerializer, RefreshSerializer
from authentication.repositories import TokenRepository
from authentication.services import (retrieve_token_service,
                                     logout_service,
                                     logout_all_service,
                                     refresh_token_service)
from authentication.validators import (is_email_valid,
                                       is_password_length_sufficient,
                                       does_contain_char_classes)

LOGGER = logging.getLogger("views")


###############################
# Helper Route Implementation #
###############################


class PasswordRequirementsView(APIView):
    """
    PasswordRequirementsView

    Returns the current server time.

    **Parameters and return value**

    :allowed: GET
    :auth required: False

    **Usage example for GET request**

    curl --request GET \
        --url 'https://api.basement.technology/auth/password.json' \
        --header 'Content-Type: application/json'

    **Return value example of GET request**

    {
    
        "minimalLength": 12,
    
        "charClasses": 3
    
    }
    """
    permission_classes = (AllowAny, )

    def get(self, request, format=None):

        user = self.request.user
        LOGGER.info(get_log_msg(self.request, user))
        content = {'minimalLength': settings.MIN_PASSWORD_LENGTH, 
                   'charClasses': settings.CHAR_CLASSES}
        return Response(content, status=status.HTTP_200_OK)


#############################
# Controller Implementation #
#############################


class UserViewSet(viewsets.ViewSet):
    """
    UserViewSet

    Provides basic operations for user instances

    **Parameters and return value**

    :allowed: GET, PATCH, DELETE
    :auth required: True

    **Usage example for GET request**

    curl --request GET \
        --url 'https://api.basement.technology/auth/users/d47947b4-65b1-11e8-87d0-c471feb11e42.json' \
        --header 'Authorization: Token db1c73de65b111e89072c471feb11e423374dea40aa196bb1dbcf88afd4dfce8' \
        --header 'Content-Type: application/json'

    **Return value example of GET request**
    {

        "id": "a9caebca-5a81-11e8-8a23-f40f2434c1ce",

        "username": "josefK1526637368",

        "email": "josefK1526637368@example.com",

        "first_name": "Josef",

        "last_name": "K"

    }
    """
    repository = GenericRepository(User)
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, )

    def retrieve(self, request, pk=None, format=None):
        """
        Builds and exposes retrieve view for users
        """
        service = generic_retrieve_single_service(self.repository)

        view = GenericViewset(self.serializer_class, service, request)
        return view.retrieve(pk)

    def list(self, request, format=None):
        """
        Builds and exposes list view for users
        """
        service = generic_retrieve_all_service(self.repository)

        view = GenericViewset(self.serializer_class, service, request)
        return view.list()


    def destroy(self, request, pk=None, format=None):
        """
        Builds and exposes destroy view for users
        """
        service = generic_delete_service(self.repository)

        view = GenericViewset(self.serializer_class, service, request)
        return view.destroy(pk)

    def partial_update(self, request, pk=None, format=None):
        """
        Builds and exposes partial update view for users
        """
        validators = (is_email_valid(self.repository),
                      is_value_unique(self.repository, 'email'),
                      is_value_unique(self.repository, 'username'),
                      is_password_length_sufficient(self.repository, settings.MIN_PASSWORD_LENGTH),
                      does_contain_char_classes(self.repository, 3))
        service = generic_update_service(self.repository, validate_many(*validators))

        view = GenericViewset(self.serializer_class, service, request)
        return view.partial_update(pk)


class RegisterViewSet(viewsets.ViewSet):
    """
    RegisterViewSet

    Provides create operation for users

    **Parameters and return value**

    :allowed: POST
    :auth required: False

    **Usage example for POST request**

    curl --request POST \
        --url https://api.basement.technology/auth/token.json \
        --header 'Content-Type: application/json' \
        --data '{

            "username": "josef1526637489",

            "password": "1Secure#Password"

        }'

    **Return value example of POST request**
    {

        "id": "f7c8aaa6-5a81-11e8-bd41-f40f2434c1ce",

        "username": "josef1526637489",

        "email": null,

        "first_name": null,

        "last_name": null

    }
    """
    repository = GenericRepository(User)
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny, )

    def create(self, request, format=None):
        """
        Builds and exposes create view for users
        """
        validators = (is_email_valid(self.repository),
                      is_value_unique(self.repository, 'id'),
                      is_value_unique(self.repository, 'email'),
                      is_value_unique(self.repository, 'username'),
                      is_password_length_sufficient(self.repository, settings.MIN_PASSWORD_LENGTH),
                      does_contain_char_classes(self.repository, settings.CHAR_CLASSES))
        service = generic_create_service(self.repository, validate_many(*validators), generic_factory)

        view = GenericViewset(self.serializer_class, service, request)
        response = view.create()
        del response.data['password']
        return response


class TokenViewSet(viewsets.ViewSet):
    """
    TokenView

    Provides api endpoint that delivers api access tokens.
    Takes username and password of :model:`authentication.User` instance.

    **Parameters and return value**

    :allowed: POST
    :auth required: False
    :many: False
    :param POST: JSON object of instance
    :returns: 200 in case of success
    :returns: token and refresh token with expiry time
    :error: 400 if posted json object is invalid
    :error: 404 if posted user could not be found
    :error: 500 if an unexpected error occurs

    **Usage example for POST request**

    curl --request POST \
        --url https://api.basement.technology/auth/token.json \
        --header 'Content-Type: application/json' \
        --data '{

            "username": "johndoe@example.com",

            "password": "John-Doe-1"

        }'

    **Return value example of POST request**

    {

        "user_id": "babda7de-6115-11e8-add9-f40f2434c1ce",

        "token": "x8bxmnsaxniz9q800h8pm554efj4l7b2u921d1c0ld66w3rf9t0rircl73rsw2va",

        "refresh_token": "th7t047ag6bnwkurqd9e81a9630ssuhuermh7qeb7vew8wand9frv6a1r9y5uu31ghpgorb0lkowv7jjta5u9691e9zfp767cypf3jzav6ppbgl2fd99idna0ndkxpis",

        "token_expiry": "2018-05-26T20:00:15.563893Z",

        "refresh_token_expiry": "2018-05-27T19:00:15.563915Z"
        
    }
    """
    permission_classes = (AllowAny, )
    serializer_class = AuthTokenSerializer
    repository = TokenRepository()

    def create(self, request, format=None):
        """
        Takes a user's username and password and generates a new token for
        that user if username and password are correct
        """
        data = request.data
        serializer = self.serializer_class(
            data=data,
            context={'request': request})

        if serializer.is_valid(raise_exception=False):
            user = serializer.validated_data['user']
            LOGGER.info(get_log_msg(self.request, user))
            return self._retrieve_token(request, user)

        LOGGER.info(get_log_msg(self.request, self.request.user))
        return self._handle_error("Validation failed", status.HTTP_400_BAD_REQUEST)

    def _retrieve_token(self, request, user):
        service = retrieve_token_service(self.repository)
        (token, refresh_token) = service(user)
        exp = get_current_datetime() + settings.TOKEN_EXPIRY
        refresh_exp = get_current_datetime() + settings.REFRESH_TOKEN_EXPIRY
        content = {'user_id': user.id,
                   'token': token,
                   'refresh_token': refresh_token,
                   'token_expiry': exp,
                   'refresh_token_expiry': refresh_exp}
        return Response(content, status=status.HTTP_200_OK)

    def _handle_error(self, e, status_code):
        content = {settings.ERROR_KEY: e}
        return Response(content, status=status_code)


class LogoutViewSet(viewsets.ViewSet):
    """
    LogoutViewSet

    Provides api endpoint that deletes the token that is passed by header.

    **Parameters and return value**

    :allowed: GET
    :auth required: True
    :many: False
    :param POST: None
    :returns: 204 in case of success

    **Usage example for GET request**

    curl --request GET \
        --url 'https://api.basement.technology/auth/logout.json' \
        --header 'Authorization: Token db1c73de65b111e89072c471feb11e423374dea40aa196bb1dbcf88afd4dfce8' \
        --header 'Content-Type: application/json'
    """
    repository = TokenRepository()

    def list(self, request, format=None):
        service = logout_service(self.repository)
        service(request.user, request._auth)
        user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class LogoutAllViewSet(viewsets.ViewSet):
    """
    LogoutViewSet

    Provides api endpoint that deletes all tokens of the logged in user.

    **Parameters and return value**

    :allowed: GET
    :auth required: True
    :many: False
    :param POST: None
    :returns: 204 in case of success

    **Usage example for GET request**

    curl --request GET \
        --url 'https://api.basement.technology/auth/logoutall.json' \
        --header 'Authorization: Token db1c73de65b111e89072c471feb11e423374dea40aa196bb1dbcf88afd4dfce8' \
        --header 'Content-Type: application/json'
    """
    repository = TokenRepository()

    def list(self, request, format=None):
        service = logout_all_service(self.repository)
        service(request.user)
        user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)
        return Response(None, status=status.HTTP_204_NO_CONTENT)

class RefreshViewSet(viewsets.ViewSet):
    """
    RefreshViewSet

    Provides api endpoint that refreshes api access tokens.
    Takes token and refresh token of :model:`authentication.AuthToken` instance.

    **Parameters and return value**

    :allowed: POST
    :auth required: True
    :many: False
    :param POST: JSON object of instance
    :returns: 200 in case of success
    :returns: token and refresh token with expiry time (see example below)
    :error: 400 if posted json object is invalid
    :error: 404 if posted user could not be found
    :error: 500 if an unexpected error occurs

    **Usage example for POST request**

    curl --request POST \
        --url 'https://api.basement.technology/auth/refresh.json' \
        --header 'Authorization: Token db1c73de65b111e89072c471feb11e423374dea40aa196bb1dbcf88afd4dfce8' \
        --header 'Content-Type: application/json' \
        --data '{

            "refresh_token": "1a958a16e9ab03489f8aa345851248d23062f9780556b2f0eb9d90c1b68adad7236fe91d72932a39619d5e72266ea9c7244fa60ff0cc868ee306072120fd0d8d"

        }'


    **Return value example of POST request**

    {

        "user_id": "babda7de-6115-11e8-add9-f40f2434c1ce",

        "token": "x8bxmnsaxniz9q800h8pm554efj4l7b2u921d1c0ld66w3rf9t0rircl73rsw2va",

        "refresh_token": "2r17z2hedt2hsjjp79g97hxyzoyuy4dw2cqcby155dwzw0bnmsiu6dlog1fprm2eno0k7c314yxh9aykvon6tefi1lh8adkzxj2fpkzjmrxzu4k23v3joj50zbyueu8z",

        "token_expiry": "2018-05-26T20:00:15.563893Z",

        "refresh_token_expiry": "2018-05-27T19:00:15.563915Z"

    }
    """
    serializer_class = RefreshSerializer
    repository = TokenRepository()

    def create(self, request, format=None):
        """
        Takes a user's refresh token and generates a new token for
        that user
        """
        data = request.data
        serializer = self.serializer_class(
            data=data,
            context={'request': request})

        if serializer.is_valid(raise_exception=False):
            token = request._auth
            refresh_token = serializer.validated_data['refresh_token']
            LOGGER.info(get_log_msg(self.request, request.user))
            return self._refresh_token(request, request.user, token, refresh_token)

        LOGGER.info(get_log_msg(self.request, self.request.user))
        return self._handle_error("Validation failed", status.HTTP_400_BAD_REQUEST)

    def _refresh_token(self, request, user, token, refresh_token):
        service = refresh_token_service(self.repository)
        (token, refresh_token) = service(user, token, refresh_token)
        exp = get_current_datetime() + settings.TOKEN_EXPIRY
        refresh_exp = get_current_datetime() + settings.REFRESH_TOKEN_EXPIRY
        content = {'user_id': user.id,
                   'token': token,
                   'refresh_token': refresh_token,
                   'token_expiry': exp,
                   'refresh_token_expiry': refresh_exp}
        return Response(content, status=status.HTTP_200_OK)

    def _handle_error(self, e, status_code):
        content = {settings.ERROR_KEY: e}
        return Response(content, status=status_code)