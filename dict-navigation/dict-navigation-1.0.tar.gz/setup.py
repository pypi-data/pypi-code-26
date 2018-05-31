import sys
from distutils.core import setup

MIN_PYTHON_VERSION = (3, 4)
if (sys.version_info[:len(MIN_PYTHON_VERSION)] < MIN_PYTHON_VERSION):
    raise SystemExit('ERROR: Python %s or higher is required, %s found.' % (
                         '.'.join(map(str,MIN_PYTHON_VERSION)),
                         '.'.join(map(str,sys.version_info[:3]))))

setup \
(
    name='dict-navigation',
    version='1.0',
    install_requires=
    [
    ],
    packages=
    [
        'dict_navigation',
    ],
    url='https://gitlab.com/Hares/dict-navigation',
    license='MIT',
    author='Peter Zaitcev / USSX-Hares',
    author_email='ussx.hares@yandex.ru',
    description='Small library for navigation in the string mappings (like parsed json)',
    keywords=[ 'dict', 'path', 'navigation', 'dict-navigation' ],
)
