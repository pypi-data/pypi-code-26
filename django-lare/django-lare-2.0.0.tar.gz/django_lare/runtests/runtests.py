import os
import sys


# adjusting sys.path
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..'))
sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_lare.test_settings'


import django
from django.conf import settings
from django.test.utils import get_runner


def usage():
    return """
    Usage: python runtests.py [UnitTestClass].[method]

    You can pass the Class name of the `UnitTestClass` you want to test.

    Append a method name if you only want to test a specific method of that class.
    """


def main():
    TestRunner = get_runner(settings)

    test_runner = TestRunner()

    test_module_name = 'django_lare.tests'
    if django.VERSION[0] == 1 and django.VERSION[1] < 6:
        test_module_name = 'tests'

    failures = test_runner.run_tests([test_module_name])

    sys.exit(failures)


if __name__ == '__main__':
    main()
