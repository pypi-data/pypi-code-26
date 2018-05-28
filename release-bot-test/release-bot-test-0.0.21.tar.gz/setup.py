try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup(
    name='release-bot-test',
    version='0.0.21',
    packages=['release_bot_test'],
    url='https://github.com/jpopelka/release-bot-test',
    license='GPLv3+',
    author='Jiri Popelka',
    author_email='jpopelka@gmail.com',
    description='test',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3'
    ],
    entry_points={'console_scripts': [
        'release-bot-test=release_bot_test.release_bot_test:main',
    ]}
)
