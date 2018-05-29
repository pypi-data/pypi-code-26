# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pendulum',
 'pendulum._extensions',
 'pendulum.formatting',
 'pendulum.locales',
 'pendulum.locales.da',
 'pendulum.locales.de',
 'pendulum.locales.en',
 'pendulum.locales.es',
 'pendulum.locales.fa',
 'pendulum.locales.fo',
 'pendulum.locales.fr',
 'pendulum.locales.ko',
 'pendulum.locales.lt',
 'pendulum.locales.pt_br',
 'pendulum.locales.zh',
 'pendulum.mixins',
 'pendulum.parsing',
 'pendulum.parsing.exceptions',
 'pendulum.tz',
 'pendulum.tz.data',
 'pendulum.tz.zoneinfo',
 'pendulum.utils']

package_data = \
{'': ['*']}

install_requires = \
['python-dateutil>=2.6,<3.0', 'pytzdata>=2018.3']

extras_require = \
{':python_version < "3.5"': ['typing>=3.6,<4.0']}

setup_kwargs = {
    'name': 'pendulum',
    'version': '2.0.2',
    'description': 'Python datetimes made easy',
    'long_description': "Pendulum\n########\n\n.. image:: https://img.shields.io/pypi/v/pendulum.svg\n    :target: https://pypi.python.org/pypi/pendulum\n\n.. image:: https://img.shields.io/pypi/l/pendulum.svg\n    :target: https://pypi.python.org/pypi/pendulum\n\n.. image:: https://img.shields.io/codecov/c/github/sdispater/pendulum/master.svg\n    :target: https://codecov.io/gh/sdispater/pendulum/branch/master\n\n.. image:: https://travis-ci.org/sdispater/pendulum.svg\n    :alt: Pendulum Build status\n    :target: https://travis-ci.org/sdispater/pendulum\n\nPython datetimes made easy.\n\nSupports Python **2.7** and **3.4+**.\n\n\n.. code-block:: python\n\n   >>> import pendulum\n\n   >>> now_in_paris = pendulum.now('Europe/Paris')\n   >>> now_in_paris\n   '2016-07-04T00:49:58.502116+02:00'\n\n   # Seamless timezone switching\n   >>> now_in_paris.in_timezone('UTC')\n   '2016-07-03T22:49:58.502116+00:00'\n\n   >>> tomorrow = pendulum.now().add(days=1)\n   >>> last_week = pendulum.now().subtract(weeks=1)\n\n   >>> past = pendulum.now().subtract(minutes=2)\n   >>> past.diff_for_humans()\n   >>> '2 minutes ago'\n\n   >>> delta = past - last_week\n   >>> delta.hours\n   23\n   >>> delta.in_words(locale='en')\n   '6 days 23 hours 58 minutes'\n\n   # Proper handling of datetime normalization\n   >>> pendulum.datetime(2013, 3, 31, 2, 30, tz='Europe/Paris')\n   '2013-03-31T03:30:00+02:00' # 2:30 does not exist (Skipped time)\n\n   # Proper handling of dst transitions\n   >>> just_before = pendulum.datetime(2013, 3, 31, 1, 59, 59, 999999, tz='Europe/Paris')\n   '2013-03-31T01:59:59.999999+01:00'\n   >>> just_before.add(microseconds=1)\n   '2013-03-31T03:00:00+02:00'\n\n\nWhy Pendulum?\n=============\n\nNative ``datetime`` instances are enough for basic cases but when you face more complex use-cases\nthey often show limitations and are not so intuitive to work with.\n``Pendulum`` provides a cleaner and more easy to use API while still relying on the standard library.\nSo it's still ``datetime`` but better.\n\nUnlike other datetime libraries for Python, Pendulum is a drop-in replacement\nfor the standard ``datetime`` class (it inherits from it), so, basically, you can replace all your ``datetime``\ninstances by ``DateTime`` instances in you code (exceptions exist for libraries that check\nthe type of the objects by using the ``type`` function like ``sqlite3`` or ``PyMySQL`` for instance).\n\nIt also removes the notion of naive datetimes: each ``Pendulum`` instance is timezone-aware\nand by default in ``UTC`` for ease of use.\n\nPendulum also improves the standard ``timedelta`` class by providing more intuitive methods and properties.\n\n\nWhy not Arrow?\n==============\n\nArrow is the most popular datetime library for Python right now, however its behavior\nand API can be erratic and unpredictable. The ``get()`` method can receive pretty much anything\nand it will try its best to return something while silently failing to handle some cases:\n\n.. code-block:: python\n\n    arrow.get('2016-1-17')\n    # <Arrow [2016-01-01T00:00:00+00:00]>\n\n    pendulum.parse('2016-1-17')\n    # <Pendulum [2016-01-17T00:00:00+00:00]>\n\n    arrow.get('20160413')\n    # <Arrow [1970-08-22T08:06:53+00:00]>\n\n    pendulum.parse('20160413')\n    # <Pendulum [2016-04-13T00:00:00+00:00]>\n\n    arrow.get('2016-W07-5')\n    # <Arrow [2016-01-01T00:00:00+00:00]>\n\n    pendulum.parse('2016-W07-5')\n    # <Pendulum [2016-02-19T00:00:00+00:00]>\n\n    # Working with DST\n    just_before = arrow.Arrow(2013, 3, 31, 1, 59, 59, 999999, 'Europe/Paris')\n    just_after = just_before.replace(microseconds=1)\n    '2013-03-31T02:00:00+02:00'\n    # Should be 2013-03-31T03:00:00+02:00\n\n    (just_after.to('utc') - just_before.to('utc')).total_seconds()\n    -3599.999999\n    # Should be 1e-06\n\n    just_before = pendulum.datetime(2013, 3, 31, 1, 59, 59, 999999, 'Europe/Paris')\n    just_after = just_before.add(microseconds=1)\n    '2013-03-31T03:00:00+02:00'\n\n    (just_after.in_timezone('utc') - just_before.in_timezone('utc')).total_seconds()\n    1e-06\n\nThose are a few examples showing that Arrow cannot always be trusted to have a consistent\nbehavior with the data you are passing to it.\n\n\nLimitations\n===========\n\nEven though the ``DateTime`` class is a subclass of ``datetime`` there are some rare cases where\nit can't replace the native class directly. Here is a list (non-exhaustive) of the reported cases with\na possible solution, if any:\n\n* ``sqlite3`` will use the ``type()`` function to determine the type of the object by default. To work around it you can register a new adapter:\n\n.. code-block:: python\n\n    from pendulum import DateTime\n    from sqlite3 import register_adapter\n\n    register_adapter(DateTime, lambda val: val.isoformat(' '))\n\n* ``mysqlclient`` (former ``MySQLdb``) and ``PyMySQL`` will use the ``type()`` function to determine the type of the object by default. To work around it you can register a new adapter:\n\n.. code-block:: python\n\n    import MySQLdb.converters\n    import pymysql.converters\n\n    from pendulum import DateTime\n\n    MySQLdb.converters.conversions[DateTime] = MySQLdb.converters.DateTime2literal\n    pymysql.converters.conversions[DateTime] = pymysql.converters.escape_datetime\n\n* ``django`` will use the ``isoformat()`` method to store datetimes in the database. However since ``pendulum`` is always timezone aware the offset information will always be returned by ``isoformat()`` raising an error, at least for MySQL databases. To work around it you can either create your own ``DateTimeField`` or use the previous workaround for ``MySQLdb``:\n\n.. code-block:: python\n\n    from django.db.models import DateTimeField as BaseDateTimeField\n    from pendulum import DateTime\n\n\n    class DateTimeField(BaseDateTimeField):\n\n        def value_to_string(self, obj):\n            val = self.value_from_object(obj)\n\n            if isinstance(value, DateTime):\n                return value.to_datetime_string()\n\n            return '' if val is None else val.isoformat()\n\n\nResources\n=========\n\n* `Official Website <https://pendulum.eustace.io>`_\n* `Documentation <https://pendulum.eustace.io/docs/>`_\n* `Issue Tracker <https://github.com/sdispater/pendulum/issues>`_\n\n\nContributing\n============\n\nContributions are welcome, especially with localization.\n\nGetting started\n---------------\n\nTo work on the Pendulum codebase, you'll want to clone the project locally\nand install the required depedendencies via `poetry <https://poetry.eustace.io>`_.\n\n.. code-block:: bash\n\n    $ git clone git@github.com:sdispater/pendulum.git\n    $ poetry install\n\nLocalization\n------------\n\nIf you want to help with localization, there are two different cases: the locale already exists\nor not.\n\nIf the locale does not exist you will need to create it by using the ``clock`` utility:\n\n.. code-block:: bash\n\n    ./clock locale:dump <your-locale>\n\nIt will generate a directory in ``pendulum/locales`` named after your locale, with the following\nstructure:\n\n.. code-block:: text\n\n    <your-locale>/\n        - custom.py\n        - locale.py\n\nThe ``locale.py`` file must not be modified. It contains the translations provided by\nthe CLDR database.\n\nThe ``custom.py`` file is the one you want to modify. It contains the data needed\nby Pendulum that are not provided by the CLDR database. You can take the `en <https://github.com/sdispater/pendulum/tree/master/pendulum/locale/en/custom.py>`_\ndata as a reference to see which data is needed.\n\nYou should also add tests for the created or modified locale.\n",
    'author': 'Sébastien Eustace',
    'author_email': 'sebastien@eustace.io',
    'url': 'https://pendulum.eustace.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
