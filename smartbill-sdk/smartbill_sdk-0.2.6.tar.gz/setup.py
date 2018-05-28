from setuptools import setup, find_packages

setup(
     name='smartbill_sdk',
     version='0.2.6',
     author='CyberAmz.com',
     author_email='office@cyberamz.com',
     classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
     ],
     keywords='smartbill api client wrapper',
     packages=find_packages(exclude=["tests"]),
     install_requires=['requests>=2.18','dicttoxml>=1.7.4', 'simplejson>=3.15.0'],
)
