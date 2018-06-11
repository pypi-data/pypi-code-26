import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name='dpp-package',
	version='0.1',
	license='MIT',
	description='Example DPP package',
	long_description=long_description,
	url='https://github.com/dorianwalega96/DPP',
	author='Dorian Walega',
	author_email='dorianwalega96@gmail.com',
	packages=setuptools.find_packages(exclude=['tests*']),
)
