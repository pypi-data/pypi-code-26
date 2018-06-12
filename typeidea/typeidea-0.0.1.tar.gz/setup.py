# coding:utf-8
from setuptools import setup, find_packages


setup(
    name='typeidea',
    version='0.0.1',
    description='Blog System base on Django',
    author='the5fire',
    author_email='thefivefire@gmail.com',
    url='https://www.the5fire.com',
    license='MIT',
    packages=find_packages('typeidea'),
    package_dir={'': 'typeidea'},
    include_package_data=True,
    install_requires=[
        'django==2.0.6',
        'uWSGI==2.0.17',
        # 'xadmin==2.0.1',
        'mysqlclient==1.3.12',
        'django-ckeditor==5.4.0',
        'django-redis==4.8.0',
        'django-autocomplete-light==3.2.10',
        'mistune==0.8.3',
        'Pillow==4.3.0',
        'django-redis==4.8.0',
        'hiredis==0.2.0',
    ],
    scripts=[
        'typeidea/manage.py',
        'typeidea/typeidea/wsgi.py',
    ],
    entry_points={
        'console_scripts': [
            'typeidea_manage = manage:main',
        ]
    },
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],

)
