from setuptools import setup

setup(name='download_openaq',
      version='0.0.3',
      description='Downloads OpenAQ CSV data from S3',
      url='',
      author='Development Seed',
      author_email='aimee@developmentseed.org,rosariosicuranza@gmail.com',
      license='MIT',
      py_modules=['download_openaq'],
      install_requires=['boto3', 'pandas'])
