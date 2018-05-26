from setuptools import setup

with open('README.md') as f:
    readme = f.read()

setup(
    name='testgokoro',
    version='0.0.1.dev2',
    packages=['testgokoro'],
    url='',
    license='MIT',
    author='gokoro',
    author_email='',
    description='testgokoro package',
    long_description=readme,
    long_description_content_type='text/markdown'
)
