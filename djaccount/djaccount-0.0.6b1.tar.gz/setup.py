from setuptools import setup, find_packages

from account import __version__

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


setup(
    name='djaccount',
    version=__version__,
    description='Django account manager',
    author='Yehuda Deutsch',
    author_email='yeh@uda.co.il',

    license='MIT',
    url='https://gitlab.com/uda/djaccount',
    keywords='django account',
    packages=find_packages(exclude=('dev',)),
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
    ],
    extras_require={
        'dev': ['django>=2.0'],
    },
    python_requires='>=3.6',
)
