"""
TestMigrations from https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations/
"""
from django.apps import apps
from django.test import TransactionTestCase
from django.db.migrations.executor import MigrationExecutor
from django.db import connection
from django.core.management import call_command


class TestMigrations(TransactionTestCase):
    """
    Modifies setUp to migrate to the migration name in `migrate_from` then run `setUpBeforeMigration(apps)`
    finally finishes migrating to `migrate_to`. Use app apps.get_model to create model objects.
    """
    @property
    def app(self):
        return apps.get_containing_app_config(type(self).__module__).name

    migrate_from = None
    migrate_to = None
    django_application = None

    def setUp(self):
        assert self.migrate_from and self.migrate_to, \
            "TestCase '{}' must define migrate_from and migrate_to properties".format(type(self).__name__)
        self.migrate_from = [(self.app, self.migrate_from)]
        self.migrate_to = [(self.app, self.migrate_to)]
        executor = MigrationExecutor(connection)
        old_apps = executor.loader.project_state(self.migrate_from).apps

        # Reverse to the original migration
        executor.migrate(self.migrate_from)

        self.setUpBeforeMigration(old_apps)

        # Run the migration to test
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()  # reload.
        executor.migrate(self.migrate_to)

        self.apps = executor.loader.project_state(self.migrate_to).apps

    def setUpBeforeMigration(self, apps):
        pass

    def tearDown(self):
        # Leave the db in the final state so that the test runner doesn't
        # error when truncating the database.
        # https://micknelson.wordpress.com/2013/03/01/testing-django-migrations/
        call_command('migrate', self.django_application, verbosity=0)


class DDSEndpointMigrationTestCase(TestMigrations):
    """
    Tests that DukeDSSettings model is migrated to DDSEndpoint
    """
    migrate_from = '0003_groupmanagerconnection'
    migrate_to = '0004_auto_20180410_1609'
    django_application = 'gcb_web_auth'

    def setUpBeforeMigration(self, apps):
        # Create a DukeDSSettings object with its common fields
        DukeDSSettings = apps.get_model('gcb_web_auth','DukeDSSettings')
        DukeDSSettings.objects.create(
            url='https://api.example.org/api',
            portal_root='https://portal.example.org',
            openid_provider_id='openid-provider-123'
          )

    def test_dukeds_settings_migrates_to_dds_endpoint(self):
        DDSEndpoint = apps.get_model('gcb_web_auth', 'DDSEndpoint')
        endpoints = DDSEndpoint.objects.all()
        self.assertEqual(len(endpoints), 1)
        endpoint = endpoints[0]
        self.assertEqual(endpoint.name, 'https://api.example.org/api')
        self.assertEqual(endpoint.api_root, 'https://api.example.org/api')
        self.assertEqual(endpoint.agent_key, '00000000000000000000000000000000')
        self.assertEqual(endpoint.portal_root, 'https://portal.example.org')
        self.assertEqual(endpoint.openid_provider_id, 'openid-provider-123')
