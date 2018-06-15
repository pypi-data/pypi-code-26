from django.test import TestCase
from .models import NavMenu
import json


class NavMenuTestCase(TestCase):
    def setUp(self):
        self.json_menu = [
            {'type': 'external_link', 'value': {'open_in_new_tab': True,
                                                'link': 'http://www.google.com', 'override_title': 'TITLE'}},
            {'type': 'page_link', 'value': {
                'open_in_new_tab': False, 'page': 2, 'override_title': ''}},
            {'type': 'image', 'value': 1},
            {'type': 'html', 'value': '<div> html is here </div>'},
            {'type': 'nav_category', 'value': {'title': 'a nav cat', 'sub_nav': [
                {'type': 'page_link', 'value': {
                    'open_in_new_tab': False, 'page': 1, 'override_title': ''}},
            ]}},
        ]
    
    def json_after_create_menu(self, json_for_create):
        menu = NavMenu.objects.create(
            name="top",
            menu=json.dumps([json_for_create])
        )
        output_json = menu.to_json()
        return json.loads(output_json)[0]

    def test_external_link(self):
        source = {
            'type': 'external_link',
            'value': {
                'open_in_new_tab': True,
                'link': 'http://www.google.com',
                'override_title': 'TITLE'
            }
        }
        expected = source
        result = self.json_after_create_menu(source)
        self.assertDictEqual(result, expected)

    def test_image(self):
        source = {'type': 'image', 'value': 1}
        expected = {'type': 'image', 'value': None}
        result = self.json_after_create_menu(source)
        self.assertDictEqual(result, expected)

    def test_html(self):
        source = {'type': 'html', 'value': '<div> html is here </div>'}
        expected = {'type': 'html', 'value': '<div> html is here </div>'}
        result = self.json_after_create_menu(source)
        self.assertDictEqual(result, expected)

    def test_page_link(self):
        source = {
            'type': 'page_link',
            'value': {
                'open_in_new_tab': False,
                'page': 2,
                'override_title': ''
            }
        }
        expected = {
            'type': 'page_link',
            'value': {
                'page': {
                    'slug': 'home',
                    'live': True,
                    'content_type': 1,
                    'pk': 2,
                    'first_published_at': None,
                    'search_description': '',
                    'numchild': 0,
                    'latest_revision_created_at': None,
                    'locked': False,
                    'expire_at': None,
                    'url': '/',
                    'show_in_menus': False,
                    'title': 'Welcome to your new Wagtail site!',
                    'seo_title': '',
                    'url_path': '/home/',
                    'depth': 2,
                    'owner': None,
                    'path': '00010001',
                    'has_unpublished_changes': False,
                    'draft_title': 'Welcome to your new Wagtail site!',
                    'expired': False,
                    'go_live_at': None,
                    'last_published_at': None,
                    'live_revision' : None,
                },
                'open_in_new_tab': False,
                'override_title': ''}
        }
        result = self.json_after_create_menu(source)
        self.assertEqual(result, expected)

    def test_nav_category(self):
        source = {
            'type': 'nav_category',
            'value': {
                'title': 'a nav cat',
                'sub_nav': [{
                    'type': 'page_link',
                    'value': {
                        'open_in_new_tab': False,
                        'page': 1,
                        'override_title': ''
                    }
                }]
            }
        }
        expected = {
            'type': 'nav_category',
            'value': {
                'title': 'a nav cat',
                'sub_nav': [{
                    'type': 'page_link',
                    'value': {
                        'page': {
                            'slug': 'root',
                            'live': True,
                            'content_type': 1,
                            'pk': 1,
                            'first_published_at': None,
                            'search_description': '',
                            'numchild': 1,
                            'latest_revision_created_at': None,
                            'locked': False,
                            'expire_at': None,
                            'show_in_menus': False,
                            'title': 'Root',
                            'seo_title': '',
                            'url_path': '/',
                            'depth': 1,
                            'owner': None,
                            'path': '0001',
                            'has_unpublished_changes': False,
                            'draft_title': 'Root',
                            'url': None,
                            'expired': False,
                            'go_live_at': None,
                            'last_published_at': None,
                            'live_revision': None,
                        },
                        'open_in_new_tab': False,
                        'override_title': ''
                    }
                }]
            }
        }
        result = self.json_after_create_menu(source)
        self.assertDictEqual(result, expected)

    def test_menu_json(self):
        """ Test serializing and deserializing the menu json """
        menu = NavMenu.objects.create(
            name="top",
            menu=json.dumps(self.json_menu)
        )

        output_json = menu.to_json()
        output = json.loads(output_json)

        self.assertEqual(output[0]['type'], "external_link")
        self.assertEqual(output[0]['value']['link'], "http://www.google.com")

    def test_render_menu(self):
        json_menu = json.dumps(self.json_menu)
        NavMenu.objects.create(name="top", menu=json_menu)
        NavMenu.objects.create(name="bottom", menu=json_menu)
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
