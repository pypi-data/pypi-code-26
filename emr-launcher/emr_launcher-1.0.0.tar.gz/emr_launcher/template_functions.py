"""
functions added to this module are added to the global template
namespace for use in templates when using emr_launcher.py. Use in
templates using jinja2 style templating  like so:

{
    "Name": "{{ my_function_in_template_functions() }}"
}
"""
import logging
from datetime import datetime, timedelta
import os
from uuid import uuid4
import pytz

logger = logging.getLogger(__name__)


def millis_to_iso(ms_epoch):
    """
        converts a given milliseconds since epoch into an iso date string
        Args:
            ms_epoch - int
        Return
            string - formatted date string
    """
    return datetime.fromtimestamp(ms_epoch/1000.0, tz=pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def uuid():
    return uuid4().hex


utc_now = datetime.utcnow()


def get_relative_date(format=None, timedelta_args=None):
    """
        Returns a formatted datetime string,
        relative to the current time,
        as ajusted by the timedelta arguments.
        Example:
            {{ get_relative_date(format='%Y-%m-01 00:00:00', timedelta_args=dict(days=-2)) }}
    """
    dt = utc_now
    if timedelta_args:
        dt = dt + timedelta(**timedelta_args)
    if format == '%s':      # for why, see http://stackoverflow.com/questions/11743019/convert-python-datetime-to-epoch-with-strftime
        str(int((dt - datetime(1970,1,1)).total_seconds()))
    return dt.strftime(format)


def get_environ():
    """
        Return the environment variables dictionary,
        Example: {{ get_environ()['USER'] }}
        A parent python program can use "os.environ[key] = value" before calling the emr launcher.
    """
    return os.environ
