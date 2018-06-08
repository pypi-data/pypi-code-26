from setuptools import setup

setup(
    name='scylla_django_session_store',
    version='0.0.2',
    packages=['tests', 'scylla_sessions', 'scylla_sessions.management',
              'scylla_sessions.management.commands'],
    url='https://github.com/mwaaas/scylla_django_session_store',
    license='MIT',
    requires=[
        "cassandra_driver (>=3.14.0)",
    ],
    author='francismwangi',
    author_email='francismwangi152@gmail.com',
    description='Syclla/Cassandra django session store. '
)
