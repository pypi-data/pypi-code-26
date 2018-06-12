import datetime
from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

from molo.core.models import SiteLanguageRelation, Languages, ArticlePage
from molo.core.tests.base import MoloTestCaseMixin

from molo.yourwords.models import (
    YourWordsCompetition, YourWordsCompetitionEntry)
from molo.yourwords.admin import (
    download_as_csv, YourWordsCompetitionEntryAdmin)
from molo.yourwords.tests.base import BaseYourWordsTestCase


class TestAdminActions(BaseYourWordsTestCase):

    def test_download_as_csv(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        comp = YourWordsCompetition(
            title='Test Competition',
            description='This is the description')
        self.competition_index.add_child(instance=comp)
        comp.save_revision().publish()

        YourWordsCompetitionEntry.objects.create(
            competition=comp,
            user=self.user,
            story_name='test',
            story_text='test body',
            terms_or_conditions_approved=True,
            hide_real_name=True
        )
        response = download_as_csv(YourWordsCompetitionEntryAdmin,
                                   None,
                                   YourWordsCompetitionEntry.objects.all())
        date = str(datetime.datetime.now().date())
        expected_output = ('id,competition,submission_date,user,story_name,'
                           'story_text,terms_or_conditions_approved,'
                           'hide_real_name,is_read,is_shortlisted,'
                           'is_winner,article_page\r\n1,Test Competition,' +
                           date + ',superuser,test,test body,'
                           'True,True,False,False,False,\r\n')
        self.assertContains(response, expected_output)

    def test_convert_to_article(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        comp = YourWordsCompetition(
            title='Test Competition',
            description='This is the description')
        self.competition_index.add_child(instance=comp)
        comp.save_revision().publish()

        entry = YourWordsCompetitionEntry.objects.create(
            competition=comp,
            user=self.user,
            story_name='test',
            story_text='test body',
            terms_or_conditions_approved=True,
            hide_real_name=True
        )

        response = self.client.get(
            '/django-admin/yourwords/yourwordscompetitionentry/%d/convert/' %
            entry.id)
        article = ArticlePage.objects.get(title='test')
        entry = YourWordsCompetitionEntry.objects.get(pk=entry.pk)
        self.assertEquals(entry.story_name, article.title)
        self.assertEquals(entry.article_page, article)
        self.assertEquals(article.body.stream_data, [
            {u'type': u'paragraph',
             u'id': entry.article_page.body.stream_data[0]['id'],
             u'value': u'Written by: Anonymous'},
            {"type": "paragraph",
             u'id': entry.article_page.body.stream_data[1]['id'],
             "value": entry.story_text}
        ])

        self.assertEquals(ArticlePage.objects.all().count(), 1)
        self.assertEquals(
            response['Location'],
            '/admin/pages/%d/move/' % article.id)

        # second time it should redirect to the edit page
        response = self.client.get(
            '/django-admin/yourwords/yourwordscompetitionentry/%d/convert/' %
            entry.id)
        self.assertEquals(
            response['Location'],
            '/admin/pages/%d/edit/' % article.id)
        self.assertEquals(ArticlePage.objects.all().count(), 1)


class TestAdminPermission(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        # create content types
        wagtailadmin_content_type, created = ContentType.objects.get_or_create(
            app_label='wagtailadmin',
            model='admin'
        )
        yourwords_content_type = ContentType.objects.get_for_model(
            YourWordsCompetitionEntry)
        # Create Wagtail admin permission
        access_admin, created = Permission.objects.get_or_create(
            content_type=wagtailadmin_content_type,
            codename='access_admin',
            name='Can access Wagtail admin'
        )
        # Create yourwords view entrie permission
        self.yourwords = Permission.objects.get(
            content_type=yourwords_content_type,
            codename='can_view_yourwords_entry')
        # create a group
        self.test_group, _ = Group.objects.get_or_create(name='Test group')
        self.test_group.permissions.add(access_admin)
        # create a user and add user to the group
        user = User.objects.create_user(
            username='username', password='password', email='login@email.com')
        user.groups.add(self.test_group)

    def test_superuser_can_see_yourwords_modeladmin(self):
        User.objects.create_superuser(
            username='super', password='password', email='login@email.com')
        self.client.login(username='super', password='password')

        response = self.client.get('/admin/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, '/admin/yourwords/yourwordscompetition/')

    def test_user_has_perm_can_view_entry_can_see_yourwords_modeladmin(self):
        self.client.login(username='username', password='password')
        user = User.objects.filter(username='username').first()

        # User shoudn't see the yourwords model admin
        self.assertTrue(user.has_perm('wagtailadmin.access_admin'))
        self.assertFalse(user.has_perm('yourwords.can_view_yourwords_entry'))
        response = self.client.get('/admin/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(
            response, '/admin/yourwords/yourwordscompetition/')

        # User shoud see the yourwords model admin
        self.test_group.permissions.add(self.yourwords)
        user = User.objects.filter(username='username').first()
        self.assertTrue(user.has_perm('wagtailadmin.access_admin'))
        self.assertTrue(user.has_perm('yourwords.can_view_yourwords_entry'))
        response = self.client.get('/admin/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, '/admin/yourwords/yourwordscompetition/')
