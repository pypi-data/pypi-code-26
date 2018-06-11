import setuptools

with open("README.md","r") as fh:
	long_description = fh.read()

setuptools.setup(
	name='pypkgdemo1',
	version='0.1',
	description='The funniest joke in the world',
	long_description=long_description,
	long_description_content_type="text/markdown",	
	url='https://github.com/tkmktime/pypkgdemo1.git',
	packages=setuptools.find_packages(),
	classifiers=[
		'Programming Language :: Python :: 2',
		'Development Status :: 4 - Beta',
		'License :: OSI Approved :: MIT License',  
	],

	author='Tim',
	author_email='tkmktime@gmail.com',
)	
