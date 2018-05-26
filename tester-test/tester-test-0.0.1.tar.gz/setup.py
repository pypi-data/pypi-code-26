import setuptools

with open('Readme.txt', 'r') as fh:
	long_desc = fh.read()


setuptools.setup(
	name="tester-test",
	version="0.0.1",
	author="femi",
	author_email="apmetdrm@gmail.com",
	description="this is simple",
	long_description=long_desc,
	url="https://github.com/anestin-femi/testing",
	classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      license='MIT',
      packages=['blendtesting'],
      include_package_data=True,
      zip_safe=False
	)