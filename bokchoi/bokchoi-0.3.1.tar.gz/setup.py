
import os
from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="bokchoi",
    version="0.3.1",
    packages=['bokchoi', 'bokchoi.aws', 'bokchoi.gcp'],
    install_requires=[
        'Click',
        'boto3',
        'botocore',
        'paramiko',
        'google-api-python-client',
        'google-auth-httplib2',
        'google-cloud-storage'
    ],
    url='https://github.com/TimNooren/bokchoi',
    author='Tim Nooren',
    author_email='timnooren@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    entry_points={
        'console_scripts': [
            'bokchoi=bokchoi.cli:cli'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
    ],
)
