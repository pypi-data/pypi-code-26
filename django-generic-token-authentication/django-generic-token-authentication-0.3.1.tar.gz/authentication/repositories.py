from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError as VE
from utility.functions import get_current_datetime
from utility.exceptions import (ObjectNotFoundError, ValidationError)
from authentication.models import AuthToken

class TokenRepository():
    """
    Provides a database abstration layer for the Token model
    """
    def delete_by_user(self, user):
        try:
            AuthToken.objects.filter(user=user).delete()
        except VE as e:
            raise ValidationError('No token passed.', field='token')

    def create_token(self, user):
        num_tokens = AuthToken.objects.filter(user=user).count()
        if num_tokens > 9:
            diff = num_tokens - 9
            keys_to_del = AuthToken.objects.filter(user=user).order_by('created')[:diff].values_list("id", flat=True)
            AuthToken.objects.filter(pk__in=list(keys_to_del)).delete()

        token = AuthToken(user=user)
        uuid = token.id
        key = token.key
        r_key = token.refresh_key
        token.key = make_password(key)
        token.refresh_key = make_password(r_key)
        token.save()
        key = uuid + key
        return (key, r_key)

    def delete_expired_tokens(self, delta):
        AuthToken.objects.filter(created__lte=get_current_datetime() - delta).delete()

    def logout(self, user, token):
        try:
            user_token = list(AuthToken.objects.filter(id=token[:32]))[0]
        except IndexError as e:
            raise ObjectNotFoundError('Object not found.', modelclass='AuthToken')
        except TypeError as e:
            raise ValidationError('No token passed.', field='token')
        
        if check_password(token[32:], user_token.key):
            user_token.delete()
            return
        else:
            raise ObjectNotFoundError('Object not found.', modelclass='AuthToken')


    def refresh_token(self, user, token, refresh_token):
        try:
            user_token = list(AuthToken.objects.filter(id=token[:32]))[0]
        except IndexError as e:
            raise ObjectNotFoundError('Object not found.', modelclass='AuthToken')
        except TypeError as e:
            raise ValidationError('No token passed.', field='token')
            
        if check_password(token[32:], user_token.key) and check_password(refresh_token, user_token.refresh_key):
            user_token.delete()
            return self.create_token(user)
        else:
            raise ObjectNotFoundError('Object not found.', modelclass='AuthToken')
