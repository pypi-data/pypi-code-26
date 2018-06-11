from setuptools import setup

setup(
    name='heiafr-hydrocontest-sensor_api',
    description='Sensor servers for Telecom Box',
    author='Jacques Supcik',
    author_email='jacques.supcik@hefr.ch',
    version='1.0.1',
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
