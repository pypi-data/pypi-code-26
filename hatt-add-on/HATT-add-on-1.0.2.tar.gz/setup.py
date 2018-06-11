__author__ = 'Tonzh'
from distutils.core import setup

setup(
    name='HATT-add-on',
    version='1.0.2',
    packages=['Core', 'Core.Action','Core.Info','Core.Lib','Core.Utils','Core.Lib.cmd'],
    url='https://pypi.org/project/HATT-add-on/',
    license='1.0.1',
    author='Tonzh',
    author_email='tong.zhang@kikatech.com',
    description="this is a second develop from HATT",
    long_description=open("README.md").read(),
    install_requires=["Queue"],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
)





