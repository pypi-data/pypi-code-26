from setuptools import setup

setup(
    name='yoyopkg',
    version='1.1',
    packages=['src', 'src.core', 'src.stores', 'src.modules'],
    url='https://github.com/ethanquix/yoyo',
    license='MIT',
    author='dwyzlic',
    author_email='dimitriwyzlic@gmail.com',
    description='A modular package manager',

    install_requires=[
   'colorama',
   'requests'
    ],

    include_package_data=True,
    entry_points={
        'console_scripts': [
            'yoyo=src:main',
        ],
    },

)
