from setuptools import setup

setup(
    name='mcsrv',
    version='1.0.12',
    install_requires=[
        "aioredis",
        "aioamqp",
        "aiopg",
        "ujson",
    ],
    description="Package for small service start",
    author='Stepan Pyzhov',
    author_email='turin.tomsk@gmail.com',
    maintainer='Stepan Pyzhov',
    packages=['mcsrv'],
    package_dir={'mcsrv': 'src'},
    url='https://github.com/Turin-tomsk/mcsrv',
)
