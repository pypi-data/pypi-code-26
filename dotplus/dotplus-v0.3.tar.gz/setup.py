from distutils.core import setup


setup(
    name='dotplus',
    packages=['dotplus'],
    version='v0.3',
    description='Client for time cards APIs',
    author='Thyago Stall',
    author_email='thstall@gmail.com',
    url='https://github.com/thyagostall/dotplus',
    download_url='https://github.com/thyagostall/dotplus/archive/v0.3.tar.gz',
    keywords=[],
    classifiers=[],
    install_requires=[
        'astroid==1.6.4',
        'attrs==18.1.0',
        'certifi==2018.4.16',
        'chardet==3.0.4',
        'idna==2.6',
        'isort==4.3.4',
        'lazy-object-proxy==1.3.1',
        'mccabe==0.6.1',
        'mock==2.0.0',
        'more-itertools==4.1.0',
        'pbr==4.0.2',
        'pluggy==0.6.0',
        'py==1.5.3',
        'pytest==3.5.1',
        'requests==2.18.4',
        'six==1.11.0',
        'urllib3==1.22',
        'wrapt==1.10.11',
    ]
)
