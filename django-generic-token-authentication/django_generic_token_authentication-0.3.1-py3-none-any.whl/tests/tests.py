from datetime import timedelta

from django.conf import settings
from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ImproperlyConfigured

from rest_framework.test import APIClient

from generic.repositories import GenericRepository
from generic.validators import validate_many

from utility.functions import (str_to_uuid1, get_current_datetime)
from utility.exceptions import (ValidationError, ObjectNotFoundError)

from authentication.repositories import TokenRepository
from authentication.models import (User, AuthToken)
from authentication.validators import (is_password_length_sufficient,
                                       does_contain_char_classes,
                                       is_email_valid)
from authentication.services import (retrieve_token_service,
                                     logout_service,
                                     logout_all_service,
                                     refresh_token_service)
from authentication.views import (PasswordRequirementsView,
                                  UserViewSet,
                                  RegisterViewSet,
                                  TokenViewSet,
                                  LogoutViewSet,
                                  LogoutAllViewSet,
                                  RefreshViewSet)

class RepositoryTest(TransactionTestCase):
    fixtures = ['init.json']

    def test_delete_by_user(self):
        repo = TokenRepository()

        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)
        num_of_tokens1 = len(list(AuthToken.objects.filter(user=user)))
        repo.delete_by_user(user)
        num_of_tokens2 = len(list(AuthToken.objects.filter(user=user)))
        self.assertEqual(num_of_tokens1-1, num_of_tokens2)

    def test_create_token(self):
        repo = TokenRepository()

        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)

        for i in range(0, 9):
            num_of_tokens1 = AuthToken.objects.filter(user=user).count()
            repo.create_token(user)
            num_of_tokens2 = AuthToken.objects.filter(user=user).count()
            self.assertEqual(num_of_tokens1+1, num_of_tokens2)

        num_of_tokens1 = AuthToken.objects.filter(user=user).count()
        repo.create_token(user)
        num_of_tokens2 =  AuthToken.objects.filter(user=user).count()
        self.assertEqual(num_of_tokens1, num_of_tokens2)

    def test_delete_expired_tokens(self):
        repo = TokenRepository()
        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)
        
        token = list(AuthToken.objects.filter(user=user))[0]
        token.created = get_current_datetime() - settings.REFRESH_TOKEN_EXPIRY - timedelta(hours=1)
        token.save()
        num_of_tokens = AuthToken.objects.filter(user=user).count()
        self.assertEqual(1, num_of_tokens)

        repo.delete_expired_tokens(settings.REFRESH_TOKEN_EXPIRY)
        num_of_tokens = AuthToken.objects.filter(user=user).count()
        self.assertEqual(0, num_of_tokens)

    def test_logout(self):
        repo = TokenRepository()
        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)
        num_of_tokens1 = AuthToken.objects.filter(user=user).count()

        (key, r_key) = repo.create_token(user)

        key2 = 'Z{0}'.format(key)
        with self.assertRaises(ObjectNotFoundError):
            repo.logout(user, key2)

        key3 = '{0}Z'.format(key)
        with self.assertRaises(ObjectNotFoundError):
            repo.logout(user, key3)

        repo.logout(user, key)
        num_of_tokens2 = AuthToken.objects.filter(user=user).count()
        self.assertEqual(num_of_tokens1, num_of_tokens2)

    def test_logout_all(self):
        repo = TokenRepository()
        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)
        
        (key, r_key) = repo.create_token(user)
        num_of_tokens1 = AuthToken.objects.filter(user=user).count()

        key2 = 'Z{0}'.format(key)
        with self.assertRaises(ObjectNotFoundError):
            repo.refresh_token(user, key2, r_key)

        key3 = '{0}Z'.format(key)
        with self.assertRaises(ObjectNotFoundError):
            repo.refresh_token(user, key3, r_key)

        repo.refresh_token(user, key, r_key)
        num_of_tokens2 = AuthToken.objects.filter(user=user).count()
        self.assertEqual(num_of_tokens1, num_of_tokens2)


class ValidatorTest(TransactionTestCase):
    fixtures = ['init.json']

    def test_is_password_length_sufficient(self):
        repo = GenericRepository(User)
        validator = is_password_length_sufficient(repo, 12)
        user = User(email='john.doe@example.com', password='1Nice#Password')

        result = validator(user)
        self.assertEqual(True, result)

        with self.assertRaises(ValidationError):
            user = User(email='john.doe@example', password='1Nice#Pass')
            result = validator(user)

        users = User.objects.all()
        result = validator(users)
        self.assertEqual(True, result)

    def test_does_contain_char_classes(self):
        repo = GenericRepository(User)
        validator = does_contain_char_classes(repo, 3)
        user = User(email='john.doe@example.com', password='1Nice#Password')

        result = validator(user)
        self.assertEqual(True, result)

        with self.assertRaises(ValidationError):
            user = User(email='john.doe@example', password='1nicepassword')
            result = validator(user)

        users = User.objects.all()
        result = validator(users)
        self.assertEqual(True, result)

        with self.assertRaises(ImproperlyConfigured):
            validator = does_contain_char_classes(repo, -1)

        with self.assertRaises(ImproperlyConfigured):
            validator = does_contain_char_classes(repo, 5)

    def test_is_email_valid(self):
        repo = GenericRepository(User)
        validator = is_email_valid(repo)
        user = User(email='john.doe@example.com', password='1Nice#Password')

        result = validator(user)
        self.assertEqual(True, result)

        with self.assertRaises(ValidationError):
            user = User(email='john.doe@example', password='1Nice#Password')
            result = validator(user)

        users = User.objects.all()
        result = validator(users)
        self.assertEqual(True, result)


class ServiceTest(TransactionTestCase):
    fixtures = ['init.json']

    def test_retrieve_token_service(self):
        repo = TokenRepository()
        retrieve = retrieve_token_service(repo)

        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)

        num_of_tokens1 = AuthToken.objects.filter(user=user).count()
        retrieve(user)
        num_of_tokens2 = AuthToken.objects.filter(user=user).count()
        self.assertEqual(num_of_tokens1+1, num_of_tokens2)

    def test_logout_service(self):
        repo = TokenRepository()
        retrieve = retrieve_token_service(repo)
        logout = logout_service(repo)

        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)

        num_of_tokens1 = AuthToken.objects.filter(user=user).count()
        (token, refresh_token) = retrieve(user)
        logout(user, token)
        num_of_tokens2 = AuthToken.objects.filter(user=user).count()
        self.assertEqual(num_of_tokens1, num_of_tokens2)

    def test_logout_all_service(self):
        repo = TokenRepository()
        logout = logout_all_service(repo)

        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)

        logout(user)
        num_of_tokens = AuthToken.objects.filter(user=user).count()
        self.assertEqual(0, num_of_tokens)

    def test_refresh_token_service(self):
        repo = TokenRepository()
        retrieve = retrieve_token_service(repo)
        refresh = refresh_token_service(repo)

        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)
        (token, refresh_token) = retrieve(user)

        num_of_tokens1 = AuthToken.objects.filter(user=user).count()
        refresh(user, token, refresh_token)
        num_of_tokens2 = AuthToken.objects.filter(user=user).count()
        self.assertEqual(num_of_tokens1, num_of_tokens2)

class ViewTest(TransactionTestCase):
    fixtures = ['init.json']

    def test_password_requirements_view(self):
        client = APIClient()
        request = client.get('/password.json', format='json')
        self.assertEqual(200, request.status_code)
        self.assertEqual(settings.MIN_PASSWORD_LENGTH, request.data['minimalLength'])
        self.assertEqual(settings.CHAR_CLASSES, request.data['charClasses'])

    def test_user_view_set(self):
        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)
        client = APIClient()
        client.force_authenticate(user=user)

        request = client.get('/users.json', format='json')
        self.assertEqual(200, request.status_code)

        request = client.get("/users/{0}.json".format(user_id), format='json')
        self.assertEqual(200, request.status_code)
        self.assertEqual(str(user_id), request.data['id'])

        name = 'New Name'
        request = client.patch("/users/{0}.json".format(user_id),
                                {'username': user.username, 'firstName': name},
                                format='json')
        self.assertEqual(200, request.status_code)
        request = client.get("/users/{0}.json".format(user_id), format='json')
        self.assertEqual(name, request.data['firstName'])

        request = client.delete("/users/{0}.json".format(user_id), format='json')
        self.assertEqual(200, request.status_code)

        request = client.get("/users/{0}.json".format(user_id), format='json')
        self.assertEqual(404, request.status_code)

    def test_register_view_set(self):
        client = APIClient()
        username = 'username'
        password = '1#Password'
        request = client.post('/register.json',
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(201, request.status_code)
        user_id = request.data['id']
        user = User.objects.get(id=user_id)
        client.force_authenticate(user=user)

        request = client.get("/users/{0}.json".format(user_id), format='json')
        self.assertEqual(username, request.data['username'])

        request = client.post('/register.json',
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(400, request.status_code)

    def test_token_view_set(self):
        client = APIClient()
        username = 'username'
        password = '1#Password'
        request = client.post('/register.json',
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(201, request.status_code)
        user_id = request.data['id']

        request = client.post('/token.json',
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(200, request.status_code)
        token = request.data['token']

        request = client.post('/token.json',
                              {'wrongKey': username, 'password': password},
                              format='json')
        self.assertEqual(400, request.status_code)

    def test_logout_view_set(self):
        client = APIClient()
        username = 'username'
        password = '1#Password'
        request = client.post("/register.json",
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(201, request.status_code)
        user_id = request.data['id']

        request = client.post("/token.json",
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(200, request.status_code)
        token = request.data['token']

        user_id = str_to_uuid1(user_id)
        user = User.objects.get(id=user_id)

        request = client.get('/logout.json', format='json')
        self.assertEqual(401, request.status_code)

    def test_logout_all_view_set(self):
        client = APIClient()
        username = 'username'
        password = '1#Password'
        request = client.post("/register.json",
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(201, request.status_code)
        user_id = request.data['id']

        request = client.post("/token.json",
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(200, request.status_code)
        token = request.data['token']

        user_id = str_to_uuid1(user_id)
        user = User.objects.get(id=user_id)

        request = client.get('/logoutall.json', format='json')
        self.assertEqual(401, request.status_code)

    def test_refresh_view_set(self):
        client = APIClient()
        username = 'username'
        password = '1#Password'
        request = client.post("/register.json",
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(201, request.status_code)

        request = client.post("/token.json",
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(200, request.status_code)
        token = request.data['token']
        refresh_token = request.data['refreshToken']

        request = client.post("/refresh.json",
                              {'refreshToken': refresh_token},
                              format='json')
        self.assertEqual(401, request.status_code)