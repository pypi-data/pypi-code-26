
from setuptools import setup, find_packages


setup(
    name='WifiZberry',
    version='0.0.1',
    author='Renan Soares',
    author_email='renansoares@live.com',
    packages=find_packages(exclude=['WifiZberry']),
    url='https://github.com/renansoaress/wifiZberry',
    description='Python API to control WiFi connectivity in Raspberry',
    zip_safe=False
)
