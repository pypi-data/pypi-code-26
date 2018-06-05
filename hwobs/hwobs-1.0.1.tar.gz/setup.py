try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(name='hwobs',
    version='1.0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'hwobs=hwobs:main',
            ]
        }
    )
