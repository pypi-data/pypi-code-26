from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='heiafr-hydrocontest-sensor_api',
    description='Sensor servers for Telecom Box',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Jacques Supcik',
    author_email='jacques.supcik@hefr.ch',
    version='1.0.2',
    license='Apache License 2.0',

    packages=['heiafr.hydrocontest.sensor_api'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: System :: Monitoring',
        'Programming Language :: Python :: 3',
    ]
)
