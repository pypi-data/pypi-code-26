from src import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='quotes-wrapper',
    version=__version__,
    description='Just Another API Wrapper',
    author='Eduardo Matos',
    author_email='eduardo.matos.silva@gmail.com',
    url='https://bitbucket.org/ematos/quotes-wrapper',
    packages=['src'],
    install_requires=['requests==2.18.4'],
)
