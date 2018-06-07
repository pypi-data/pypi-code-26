from setuptools import setup
setup(
    name='apscheduler_bundle',
    packages=['apscheduler_bundle'],
    version='1.1',
    description='APScheduler support for applauncher',
    author='Alvaro Garcia Gomez',
    author_email='maxpowel@gmail.com',
    url='https://github.com/applauncher-team/apscheduler_bundle',
    download_url='https://github.com/applauncher-team/apscheduler_bundle',
    keywords=['applauncher', 'apscheduler', 'scheduler'],
    classifiers=['Topic :: Adaptive Technologies', 'Topic :: Software Development', 'Topic :: System',
                 'Topic :: Utilities'],
    install_requires=['applauncher', 'apscheduler']
)
