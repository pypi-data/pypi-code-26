from setuptools import setup

setup(
	name='testpotato',
	version='1.0.1',
	description='pypi testing',
	packages=['potatofieldd'],
	entry_points={
	    'console_scripts': [
	        'potato=potatofieldd.potato:run',
	        'potatofield=potatofieldd.potato:run'
	    ]
	}
)
