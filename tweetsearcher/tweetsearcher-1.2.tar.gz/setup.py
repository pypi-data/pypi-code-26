from setuptools import setup, find_packages

setup(
    name='tweetsearcher',
    packages=['tweetsearcher'],
    version='1.2',
    description='Library to bypass limitations of the Twitter Official API',
    author='Alexander Hudym',
    author_email='alexanderhudym@gmail.com',
    url='https://github.com/alexanderhudym/tweet-searcher',
    download_url='https://github.com/alexanderhudym/tweet-searcher/archive/1.0.tar.gz',
    keywords=['tweet', 'twitter', 'search', 'old'],
    classifiers=[],
    install_requires=[
        'lxml', 'requests', 'PySocks', 'beautifulsoup4',
    ],
)
