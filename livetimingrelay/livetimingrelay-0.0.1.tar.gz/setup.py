from setuptools import setup, find_packages

setup(
    name='livetimingrelay',
    version='0.0.1',
    description='Relay for Live Timing Aggregator',
    author='James Muscat',
    author_email='jamesremuscat@gmail.com',
    url='https://timing.71wytham.org.uk/',
    packages=find_packages('src', exclude=["*.tests"]),
    package_dir={'': 'src'},
    long_description="Relay for Live Timing Aggregator. To set up a relay please contact timing@71wytham.org.uk.",
    install_requires=[
        "autobahn[twisted]>=17.6.2",
        "crossbar==18.4.1"
    ]
)
