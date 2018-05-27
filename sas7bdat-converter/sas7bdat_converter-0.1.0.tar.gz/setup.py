from setuptools import setup
from setuptools import find_packages

#with open("README.md", "r") as fh:
#    long_description = fh.read()
long_description = '''
Converts proprietary sas7bdat files from SAS into formats such as csv and XML useable by other programs. Currently supported conversiaions are csv, Excel (xlsx format), json, Pandas DataFrame, and XML.

Conversions can be done on either a single file or a batch of files.
'''

setup(
    name='sas7bdat_converter',
    version='0.1.0',
    author='Paul Sanders',
    author_email='psanders1@gmail.com',
    license='Apache 2.0',
    #long_description_content_type='text/markdown',
    description='Convert sas7bdat files into other formats',
    long_description=long_description,
    url='https://github.com/sanders41/sas7bdat_converter',
    download_url='https://github.com/sanders41/sas7bdat_converter/archive/v0.1.0.tar.gz',
    install_requires=['pandas>=0.23.0',
                      'XlsxWriter>=1.0.5'],
    extras_require={
        'test': ['xlrd>=1.1.0'],
    },
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent'
    ],
)
