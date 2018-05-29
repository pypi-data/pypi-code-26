from django.test import TestCase, RequestFactory, TransactionTestCase

from tabula_auth.backends.phone_backend import PhoneBackend
from tabula_auth.models import PhoneToken, PhoneNumberUser

from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from freezegun import freeze_time
import datetime
from tabula_auth.exceptions import TabulaAuthException


# Create your tests here.

class CreateOtpTestCase(TestCase):
    initial_date = datetime.datetime(
        year=2018,
        month=1,
        day=2,
        hour=10,
        minute=10,
        second=10)

    def testCreateOtp(self):
        from .models import PhoneToken
        number = '+79146682876'
        token, otp = PhoneToken.create_otp_for_number(number)
        token.check_otp(otp)
        self.assertTrue(token.check_otp(otp))

    @freeze_time(initial_date, as_arg=True)
    def testCreateALotOtp(frozen_time, self):
        from .models import PhoneToken
        number = '+79146682876'
        otp = ""
        new_time = self.initial_date
        try:
            for _ in range(20):
                frozen_time.move_to(new_time)
                token, otp = PhoneToken.create_otp_for_number(number)
                new_time += datetime.timedelta(seconds=125)
        except TabulaAuthException as e:
            self.assertTrue(e.error_type, 'login_attempts')

    @freeze_time(initial_date, as_arg=True)
    def testCreateOtpWithoutRemainTime(frozen_time, self):
        from .models import PhoneToken
        number = '+79146682876'
        otp = ""
        new_time = self.initial_date
        try:
            for _ in range(5):
                frozen_time.move_to(new_time)
                token, otp = PhoneToken.create_otp_for_number(number)
                new_time += datetime.timedelta(seconds=20)
        except TabulaAuthException as e:
            self.assertTrue(e.error_type, 'time_remain')

    @freeze_time(initial_date, as_arg=True)
    def testCreateOtpOn2numbers(frozen_time, self):
        from .models import PhoneToken
        number1 = '+79146682876'
        number2 = '+79146682936'
        new_time = self.initial_date
        for i in range(14):
            frozen_time.move_to(new_time)
            number = number1 if i % 2 else number2
            token, otp = PhoneToken.create_otp_for_number(number)
            new_time += datetime.timedelta(seconds=200)
            self.assertTrue(otp)


class PhoneBackendTest(TransactionTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        super(PhoneBackendTest, self).setUp()

    def test_initialization(self):
        phonebackend = PhoneBackend()
        User = phonebackend.user_model
        self.assertEqual(User.objects.count(), 0)

    def test_authenticate_registration(self):
        phonebackend = PhoneBackend()
        phone_number = "+18609409290"
        token, otp = PhoneToken.create_otp_for_number(phone_number)
        user = phonebackend.authenticate(
            request=self.factory.get(''), pk=token.id, otp=otp)
        self.assertEqual(user.phone_number, phone_number, 'Signup phonenumber')

    def test_authenticate_login(self):
        phonebackend = PhoneBackend()
        phone_number = "+18609409290"
        phone_token, otp = PhoneToken.create_otp_for_number(phone_number)
        user = phonebackend.create_user(
            phone_token=phone_token
        )
        self.assertEqual(user.phone_number, phone_number, 'User creation')
        authenticated_user = phonebackend.authenticate(
            request=self.factory.get(''),
            pk=phone_token.id,
            otp=otp
        )
        self.assertEqual(
            authenticated_user.phone_number,
            phone_number,
            'Login phonenumber'
        )


class AcceptTermsTest(APITestCase):

    def setUp(self):
        self.factory = RequestFactory()
        super(self.__class__, self).setUp()
        self.phonebackend = PhoneBackend()

        phone_number = "+18609409290"
        phone_token, otp = PhoneToken.create_otp_for_number(phone_number)
        self.user = self.phonebackend.create_user(
            phone_token=phone_token
        )
        url = reverse('tabula_auth:validate')

        data = {
            "pk": phone_token.pk,
            "otp": otp
        }
        response = self.client.post(url, data, format='json')
        token = response.data['token']
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def test_accept_terms(self):
        url = reverse('tabula_auth:accept_terms')
        data = {
            'accept_terms': True
        }
        response = self.client.post(url, data=data, format='json')
        self.assertTrue(response.data['accept_terms'])


class GetDeleteUserTest(APITestCase):

    def setUp(self):
        self.factory = RequestFactory()
        super(self.__class__, self).setUp()
        self.phonebackend = PhoneBackend()

        phone_number = "+18609409290"
        phone_token, otp = PhoneToken.create_otp_for_number(phone_number)
        self.user = self.phonebackend.create_user(
            phone_token=phone_token
        )
        url = reverse('tabula_auth:validate')

        data = {
            "pk": phone_token.pk,
            "otp": otp
        }
        response = self.client.post(url, data, format='json')
        token = response.data['token']
        self.user_id = response.data['id']
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def test_get_user(self):
        url = reverse('tabula_auth:user')

        response = self.client.get(url, format='json')

        self.assertFalse(response.data['accept_terms'])

    def test_delete_user(self):
        url = reverse('tabula_auth:gdpr')

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(PhoneNumberUser.objects.count(), 0)


class ChangeNumberTest(APITestCase):

    def setUp(self):
        self.factory = RequestFactory()
        super(self.__class__, self).setUp()
        self.phonebackend = PhoneBackend()

        phone_number = "+18609409290"
        phone_token, otp = PhoneToken.create_otp_for_number(phone_number)
        user = self.phonebackend.create_user(
            phone_token=phone_token
        )
        url = reverse('tabula_auth:validate')

        data = {
            "pk": phone_token.pk,
            "otp": otp
        }
        response = self.client.post(url, data, format='json')
        token = response.data['token']
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
