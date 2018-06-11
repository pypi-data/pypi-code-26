from typing import Tuple
from unittest import mock
import pytest
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils.six import StringIO
from yagura.monitors import models, services


class MockResponse(object):
    def __init__(self, status_code):
        self.code = status_code


def mocked_urlopen(*args, **kwargs):
    from urllib.error import HTTPError
    url = args[0]
    if url[-3:] == '200':
        return MockResponse(200)
    raise HTTPError(url=url, code=404, msg='Failure', hdrs='', fp=StringIO())


def run_command(command: str, *args) -> Tuple[StringIO, StringIO]:
    from django.core.management import call_command
    out = StringIO()
    err = StringIO()
    call_command(command, *args, stdout=out, stderr=err)
    return out, err


class TargetState_ModelTest(TestCase):
    fixtures = [
        'unittest_sites',
    ]

    def test_str(self):
        from django.utils.timezone import now
        target = models.Target.objects.first()
        state = models.TargetState(target=target, begin_at=now())
        assert 'http://example.com' in str(state)
        assert 'None' not in str(state)


class MonitorSite_CommandTest(TestCase):
    fixtures = [
        'unittest_sites',
    ]

    def test_not_uuid(self):
        with pytest.raises(CommandError) as err:
            run_command('monitor_site', '1')
        assert 'must be UUID' in str(err)

    def test_site_not_in_db(self):
        test_uuid = 'aaaaaaaa-bbbb-4ccc-dddd-eeeeeeeeee00'
        with pytest.raises(CommandError) as err:
            run_command('monitor_site', test_uuid)
        assert 'not found' in str(err)

    @mock.patch(
        'yagura.monitors.services.urlopen',
        side_effect=mocked_urlopen
    )
    def test_site_found(self, mock_get):
        test_uuid = 'aaaaaaaa-bbbb-4ccc-dddd-eeeeeeeeee01'
        out, err = run_command('monitor_site', test_uuid)
        assert 'OK' in out.getvalue()
        assert models.TargetState.objects.count() == 1
        state = models.TargetState.objects.first()
        assert state.state == 'OK'

    @mock.patch(
        'yagura.monitors.services.urlopen',
        side_effect=mocked_urlopen
    )
    def test_site_not_found(self, mock_get):
        test_uuid = 'aaaaaaaa-bbbb-4ccc-dddd-eeeeeeeeee02'
        out, err = run_command('monitor_site', test_uuid)
        assert 'NG' in out.getvalue()
        assert models.TargetState.objects.count() == 1
        state = models.TargetState.objects.first()
        assert state.state == 'NG'

    @mock.patch(
        'yagura.monitors.services.urlopen',
        side_effect=mocked_urlopen
    )
    def test_keep_state(self, mock_get):
        self.test_site_found()
        before_updated = models.TargetState.objects.first().updated_at
        test_uuid = 'aaaaaaaa-bbbb-4ccc-dddd-eeeeeeeeee01'
        out, err = run_command('monitor_site', test_uuid)
        assert models.TargetState.objects.count() == 1
        after_updated = models.TargetState.objects.first().updated_at
        assert before_updated != after_updated

    @mock.patch(
        'yagura.monitors.services.urlopen',
        side_effect=mocked_urlopen
    )
    def test_change_state(self, mock_get):
        from yagura.sites.models import Site
        test_uuid = 'aaaaaaaa-bbbb-4ccc-dddd-eeeeeeeeee01'
        self.test_site_found()
        site = Site.objects.first()
        site.url += '/404'
        site.save()
        out, err = run_command('monitor_site', test_uuid)
        assert models.TargetState.objects.count() == 2
        before = models.TargetState.objects.first()
        # after = models.TargetState.objects.last()
        assert before.end_at is not None


class MonitorAll_CommandTest(TestCase):
    fixtures = [
        'unittest_sites',
    ]

    @mock.patch(
        'yagura.monitors.services.urlopen',
        side_effect=mocked_urlopen
    )
    def test_save_all_states(self, mock_get):
        out, err = run_command('monitor_all')
        assert models.TargetState.objects.count() == 2

    @mock.patch(
        'yagura.monitors.services.urlopen',
        side_effect=mocked_urlopen
    )
    def test_states_not_changed(self, mock_get):
        self.test_save_all_states()
        out, err = run_command('monitor_all')
        assert models.TargetState.objects.count() == 2


class SaveState_ServiceTest(TestCase):
    fixtures = [
        'unittest_sites',
    ]

    def test_it(self):
        target = models.Target.objects.first()
        state = services.save_state(target, 'OK')
        assert models.TargetState.objects.count() == 1
        assert state.state == 'OK'

    def test_same_state(self):
        self.test_it()
        target = models.Target.objects.first()
        services.save_state(target, 'OK')
        assert models.TargetState.objects.count() == 1

    def test_change_state(self):
        self.test_it()
        target = models.Target.objects.first()
        services.save_state(target, 'NG')
        assert models.TargetState.objects.count() == 2
