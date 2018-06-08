import setuptools


setuptools.setup(
    name='edb',
    version='0.0.2',
    description='Core EdgeDB Namespace',
    long_description='Core EdgeDB Namespace',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ],
    author='MagicStack Inc',
    author_email='hello@magic.io',
    url='https://github.com/edgedb/edgedb',
    license='Apache License, Version 2.0',
    packages=['edb'],
    provides=['edb'],
    include_package_data=True,
)
