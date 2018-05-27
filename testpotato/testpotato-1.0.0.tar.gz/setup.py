from setuptools import setup

setup(
	name='testpotato',
	version='1.0.0',
	description='pypi testing',
	packages=['potatofield'],
	entry_points={
	    'console_scripts': [
	        'potato=potatofield.potato:run',
	        'potatofield=potatofield.potato:run'
	    ]
	}
)
