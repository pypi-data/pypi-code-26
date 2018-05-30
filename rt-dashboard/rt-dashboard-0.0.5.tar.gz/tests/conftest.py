import pytest

from redis_tasks.conf import settings as rt_settings


def pytest_configure(config):
    rt_settings.configure_from_dict(dict(
        REDIS_PREFIX="rt_dashboard_test"))


@pytest.fixture(scope="session")
def app():
    from rt_dashboard.web import app
    return app
