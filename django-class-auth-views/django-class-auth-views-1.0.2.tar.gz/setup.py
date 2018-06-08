from setuptools import setup, find_packages

from class_based_auth_views.version import get_version

setup(
    name="django-class-auth-views",
    version=get_version(),
    url='https://github.com/druids/django-class-based-auth-views',
    license='BSD',
    platforms=['OS Independent'],
    description="A reimplementation of django.contrib.auth.views as class based views.",
    long_description=open('README.rst').read(),
    author='Stefan Foulis',
    author_email='stefan@foulis.ch',
    maintainer='Stefan Foulis',
    maintainer_email='stefan@foulis.ch',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
