import os
from setuptools import setup

import codenerix_vending

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-codenerix-vending',
    version=codenerix_vending.__version__,
    packages=["codenerix_vending"],
    include_package_data=True,
    zip_safe=False,
    license='Apache License Version 2.0',
    description='Codenerix Vending is a module that enables CODENERIX to work a Point Of Sales system focused for business faced to final client (services, supermarkets & shops, examples: retaurants, petrol stations, clothes shops, grocery store, hardware store and others).',
    long_description=README,
    url='https://github.com/codenerix/django-codenerix-vending',
    author=", ".join(codenerix_vending.__authors__),
    keywords=['django', 'codenerix', 'management', 'erp', 'crm', 'vending'],
    platforms=['OS Independent'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'django-codenerix',
        'django-codenerix-extensions',
        'django-codenerix-invoicing',
        'django-codenerix-products',
        'django-codenerix-pos',
    ]
)
