import setuptools

with open("README.md","r") as fh:
	long_description = fh.read()

setuptools.setup(
	name='pypkgdemo1',
	version='0.2',
	description='The funniest joke in the world',
	long_description=long_description,
	long_description_content_type="text/markdown",	
	packages=setuptools.find_packages(),
	url='https://github.com/tkmktime/pypkgdemo1.git',
	author='Tim',
	author_email='tkmktime@gmail.com',
	classifiers=[
		'Programming Language :: Python :: 2',
		'Development Status :: 4 - Beta',
		'License :: OSI Approved :: MIT License',  
	],
)	



# Usage:
# python setup.py sdist bdist_wheel
# twine upload dist/*