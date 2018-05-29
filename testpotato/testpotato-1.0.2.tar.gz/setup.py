from setuptools import setup

setup(
	name='testpotato',
	version='1.0.2',
	description='This is very usual todo-list',
	packages=['potatodata'],
	entry_points={
	    'console_scripts': [
	        'potato=potatodata.potato:run',
	        'potatofield=potatodata.potato:run'
	    ]
	}
)
