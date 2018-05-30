import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'djangoplus/README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='djangoplus',
    version='0.0.56',
    packages=find_packages(),
    install_requires=['Django==2.0.3', 'setuptools==39.0.1', 'cryptography==2.2.1', 'Pillow==5.0.0', 'xhtml2pdf==0.2.1', 'python-dateutil==2.7.1', 'gunicorn==19.7.1', 'selenium==3.11.0', 'xlwt==1.3.0', 'xlrd==1.1.0', 'unicodecsv==0.14.1', 'dropbox==8.7.1', 'Fabric3==1.14.post1', 'qrcode==6.0'],
    scripts=['djangoplus/bin/startproject', 'djangoplus/bin/runserver', 'djangoplus/bin/sync'],
    include_package_data=True,
    license='BSD License',
    description='Metadata-based web framework for the development of management information systems',
    long_description='',  # README
    url='http://djangoplus.net/',
    author='Breno Silva',
    author_email='brenokcc@yahoo.com.br',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
