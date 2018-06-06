from setuptools import setup

try:
	from pypandoc import convert_file
	long_description  = convert_file('README.md','md')

except ImportError:
	long_description = """ 
	
	Rishab - Python Packages
	Copyright @ 2018 - http://www.rishab.co

	Warning: Use without Permission of the authors is restricted and  if permission is granted please Cite as Rishab Sharma @ CSE  MAIT, GGSIPU New, Delhi
	
	"""

setup(name = 'rishab',
	description = 'A library to auto construct DL Models using an API service',
	long_description = long_description,
	version = '0.0.1',
	url = 'https://github.com/rishab-sharma/rishab.git',
	author = 'Rishab Sharma',
	author_email = 'rishabsharmaddn@gmail.com',
	license = 'MIT',
	classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 2'
      ],
      packages=['rishab'],
      install_requires=[
          'keras>=2.1.2',
          'flask>=0.12'
      ],
      entry_points={
          'console_scripts': [
              'encrypt=crytto.main:encrypt_cmd',
              'decrypt=crytto.main:decrypt_cmd',
              'prune_store=crytto.main:prune_cmd',
              'encrypt_send=crytto.main:send_cmd'
          ]
  })

