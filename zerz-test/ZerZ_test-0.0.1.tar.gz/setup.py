import setuptools

with open('README.md', mode='r') as fh:
	long_description = fh.read()

setuptools.setup(
	name='ZerZ_test',
	version='0.0.1',
	author='Example Author',
	author_email='author@example.com',
	description='A sma;; exmaple package',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/pypa/example-project',
	packages=setuptools.find_packages(),
	classfilters=(
			'Programmin Language :: Python :: 3',
			'License:: OSI Approved :: MIT License',
			'Operating System :: OS Independent',
		),
)