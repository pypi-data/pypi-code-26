
import codecs
from setuptools import setup, find_packages

REQUIREMENTS = [
    'six>=1.10.0',
    'json_checker==1.2.0',
    'requests>=2.9.1',
    'py>=1.5.2',
    'pytest>=3.2.3',
    'pytest-xdist>=1.22.0',
    'pytest-html>=1.11.0',
    'pytest_rerunfailures>=2.1.0',
    'pytest-forked>=0.2',
    'pytest-instafail>=0.3.0',
]


setup(
    name='Promium',
    version='0.0.2',
    install_requires=REQUIREMENTS,
    author='Denis Korytkin',
    description='Selenium wrapper for testing Web UI',
    long_description=codecs.open('README.rst', 'r', 'utf-8').read(),
    keywords=['Testing UI', 'Selenium', 'PageObject', 'Selenium wrapper'],
    platforms=['linux'],
    packages=find_packages(),
    entry_points={'pytest11': ['promium = promium.plugin']},
    python_requires='>=2.7',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Testing'
    ]
)
