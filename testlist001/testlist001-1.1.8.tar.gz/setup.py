from setuptools import setup

setup(
	name='testlist001',
	version='1.1.8',
	description='pypi testing',
	packages=['potatofield'],
	entry_points={
	    'console_scripts': [
	        'potato=potatofield.potato:run',
	        'potatofield=potatofield.potato:run'
	    ]
	}
)
