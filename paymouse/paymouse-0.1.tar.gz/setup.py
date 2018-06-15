from setuptools import setup


def readme():
    with open('README.md') as input_file:
        return input_file.read()


setup(name='paymouse',
      version='0.1',
      description='Python multiple payment gateway',
      long_description=readme(),
      long_description_content_type='text/markdown',
      keywords='payments',
      url='https://github.com/markypython/paymouse',
      author='Mark Skelton',
      author_email='mdskelton99@gmail.com',
      license='MIT',
      packages=['paymouse'],
      install_requires=[
          'stripe',
          'authorizenet'
      ],
      zip_safe=False)
