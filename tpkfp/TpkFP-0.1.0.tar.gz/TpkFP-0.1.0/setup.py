from distutils.core import setup

setup(
    name='TpkFP',
    version='0.1.0',
    author='Thaduri Pranabh Kumar',
    author_email='pranabhkumar@gmail.com',
    packages=['tpkfp', 'tpkfp.test'],
    url='http://pypi.python.org/pypi/TowelStuff/',
    license='LICENSE.txt',
    description='Useful towel-related stuff.',
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >= 1.1.1",
        "caldav == 0.1.4",
    ],
)
