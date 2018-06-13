from setuptools import setup

install_requires = [
    'boto3==1.7.0',
    'baker==1.3'
]

setup(name='envtransformer',
      version='0.1',
      description='Environment Variable Swapper',
      url='https://github.com/nimboya/envtransformer',
      author='Ewere Diagboya',
      author_email='nimboya@gmail.com',
      license='Apache License 2.0',
      packages=['envtransformer'],
      zip_safe=False)

