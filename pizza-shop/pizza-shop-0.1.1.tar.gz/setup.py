from setuptools import setup

setup(
    name = 'pizza-shop',
    version = '0.1.1',
    packages = ['pizzashop'],
	entry_points = { 'console_scripts': ['pizza-shop=pizzashop.main:main'] },
	author = "jacksonelfers",
    author_email = "JacksonElfers@hotmail.com",
	package_data = { 'pizzashop': ['stories/*.txt'] },
    license = 'Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description = open('README.txt').read()
)