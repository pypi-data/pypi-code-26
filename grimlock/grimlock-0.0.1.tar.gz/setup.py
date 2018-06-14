import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="grimlock",
	version="0.0.1",
	author="Matt Moody",
	author_email="matt@bellwethr.com",
	description="Simple tool that assists with preprocessing pandas dataframes for Machine Learning.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/BellwethrInc/grimlock",
	packages=setuptools.find_packages(),
	install_requires=[
		'numpy',
		'pandas',
	],
	classifiers=(
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	),
)