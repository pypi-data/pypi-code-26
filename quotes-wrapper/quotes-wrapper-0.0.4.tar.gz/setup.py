try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='quotes-wrapper',
    version='0.0.4',
    description='Just Another API Wrapper',
    author='Eduardo Matos',
    author_email='eduardo.matos.silva@gmail.com',
    url='https://bitbucket.org/ematos/quotes-wrapper',
    packages=['quotes_wrapper'],
    install_requires=['requests==2.18.4'],
)
