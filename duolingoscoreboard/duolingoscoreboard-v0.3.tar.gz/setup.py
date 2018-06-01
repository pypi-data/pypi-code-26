from distutils.core import setup

setup(
    name='duolingoscoreboard',
    packages=['scoreboard'],
    version='v0.3',
    description='Client for time cards APIs',
    author='Thyago Stall',
    author_email='thstall@gmail.com',
    url='https://github.com/thyagostall/duolingoscoreboard',
    download_url='https://github.com/thyagostall/duolingoscoreboard/archive/v0.3.tar.gz',
    keywords=[],
    classifiers=[],
    install_requires=[
        'certifi==2018.4.16',
        'chardet==3.0.4',
        'idna==2.6',
        'requests==2.18.4',
        'urllib3==1.22',
    ]
)
