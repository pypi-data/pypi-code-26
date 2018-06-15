import setuptools

from distutils.core import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst', format='md')
except Exception:
    long_description = 'See http://pypi.python.org/pypi/datalab-utils/'


about = {}
with open('datalab_utils/__about__.py') as fp:
    exec(fp.read(), about)

setup(
    name='datalab-utils',
    packages=setuptools.find_packages(),
    version=about['version'],
    description='Datalab Utils is a module with some convenient utilities to work with GCP datalabs.',
    long_description=long_description,
    author='Pierre Merienne',
    license='BSD',
    url='https://github.com/pmerienne/datalab-utils',
    download_url='https://github.com/pmerienne/datalab-utils/archive/%s.tar.gz' % about['version'],
    keywords=['google datalab', 'bigquery', 'utils'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=[
        'requests>=2.18.4',
        'tqdm>=4.23.2',
        'google-api-python-client>=1.7.3',
        'google-cloud-bigquery>=1.3.0',
        'google-cloud-storage>=1.10.0',
        'oauth2client>=3.0.0',
        'pandas-gbq>=0.4.1'
    ],
    setup_requires=[
        'pypandoc>=1.4'
    ]
)
