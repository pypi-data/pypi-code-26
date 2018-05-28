from django.contrib.auth.models import User
from django.core import mail
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient
import json
import re
from .models import Ticket


class TestTicketAPI(APITestCase):
    PASSWORD = 'secret'

    def setUp(self):
        super().setUp()

        # Create users
        self.user = User.objects.create_user('user@random.com', email='user@random.com', password=self.PASSWORD)
        self.admin = User.objects.create_superuser('admin@business.com', email='admin@business.com',
                                                   password=self.PASSWORD)

        self.authenticated_ticket = {
            'subject': 'Hello',
            'text': 'I have a problem',
            'meta': {
                'page': '/blog/1'
            }
        }

        self.anon_ticket = {
            'email': 'anonym@mail.com',
            'subject': 'Hello',
            'text': 'I have a problem',
            'meta': {
                'page': '/blog/1'
            }
        }
        # Set clients
        self.user_client = APIClient()
        self.user_client.login(username='user@random.com', password=self.PASSWORD)
        self.anon_client = APIClient()
        self.admin_client = APIClient()
        self.admin_client.login(username='admin@business.com', password=self.PASSWORD)

    def test_create_user_ticket(self):
        url = reverse('ticket-create')
        response = self.user_client.post(url, self.authenticated_ticket, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['text'], 'I have a problem')
        self.assertEqual(response.data['assignee'], None)

    def test_create_user_ticket_text_required(self):
        url = reverse('ticket-create')
        data = {
            'subject': 'Hello',
        }
        response = self.user_client.post(url, data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'text': ['This field is required.']})

    def test_create_user_ticket_subject_required(self):
        url = reverse('ticket-create')
        data = {
            'text': 'I have a problem',
        }
        response = self.user_client.post(url, data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'subject': ['This field is required.']})

    def test_create_anonym_ticket(self):
        url = reverse('ticket-create')

        response = self.anon_client.post(url, self.anon_ticket, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user'], None)
        self.assertEqual(response.data['text'], 'I have a problem')

    def test_create_user_ticket_notify_superusers(self):
        url = reverse('ticket-create')

        response = self.user_client.post(url, self.authenticated_ticket, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(mail.outbox[0].subject, 'New ticket has been submitted')
        self.assertIn('I have a problem', mail.outbox[0].message().as_string())

    def test_tickets_meta_retrieve_403_for_anon(self):
        ticket = Ticket.objects.create(**self.anon_ticket)
        url = reverse('ticket-meta-download', args=[ticket.id])
        response = self.anon_client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_tickets_meta_retrieve_403_for_user(self):
        ticket = Ticket.objects.create(**self.anon_ticket)
        url = reverse('ticket-meta-download', args=[ticket.id])
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_tickets_meta_retrieve_200_for_admin(self):
        ticket = Ticket.objects.create(**self.anon_ticket)
        url = reverse('ticket-meta-download', args=[ticket.id])
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_tickets_meta_retrieve_return_meta_as_downloadable_json(self):
        ticket = Ticket.objects.create(**self.anon_ticket)
        url = reverse('ticket-meta-download', args=[ticket.id])
        attachment_name = re.sub(r'\s+', '_', self.anon_ticket.get('subject'))
        response = self.admin_client.get(url)
        content_type = response._headers.get('content-type')
        content_disposition = response._headers.get('content-disposition')
        self.assertEqual(json.loads(response.content), self.anon_ticket.get('meta'))
        self.assertEqual(content_type, ('Content-Type', 'application/json'))
        self.assertEqual(content_disposition, ('Content-Disposition', 'attachment; filename={}.json'.format(attachment_name)))



