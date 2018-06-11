import claptrap

from setuptools import setup

setup(
    name='claptrap',
    version=claptrap.__version__,
    description='Spew words using bigram frequencies',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nicktimko/claptrap',

    author='Nick Timkovich',
    author_email='prometheus235@gmail.com',

    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    packages=['claptrap'],
)
