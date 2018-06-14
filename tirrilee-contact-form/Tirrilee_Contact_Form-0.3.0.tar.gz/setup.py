import os, ssl
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

setup(
    name='Tirrilee_Contact_Form',
    version='0.3.0',
    packages=['Tirrilee_Contact_Form/templates', 'Tirrilee_Contact_Form/templatetags', 'Tirrilee_Contact_Form'],
    description='Contact Form Package From Tirrilee',
    long_description=README,
    long_description_content_type="text/markdown",
    author='Aiden',
    author_email='aiden@tirrilee.io',
    url='https://github.com/Tirrilee/Django-Packages/Contact-Form/',
    license='MIT',
    include_package_data=True,
    install_requires=[
        'Django>=2.0',
    ]
)