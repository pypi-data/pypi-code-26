from setuptools import setup

setup(
	name='testpotato',
	version='2.5.6',
	description='This is very usual todo-list',
	author = 'Team_potato',
	packages=['ppo'],
	python_requires = '>=3.6',
	entry_points={
	    'console_scripts': [
	        'potato=ppo.potato:run',
	        'potatofield=ppo.potato:run'
	    ]
	},
	classifiers=['Programming Language :: Python :: 3.6']
)
