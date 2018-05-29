from setuptools import setup

setup(
	name='testpotato',
	version='1.0.3',
	description='This is very usual todo-list',
	packages=['potatodat'],
	entry_points={
	    'console_scripts': [
	        'potato=potatodat.potato:run',
	        'potatofield=potatodat.potato:run'
	    ]
	}
)
