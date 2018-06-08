#!/usr/bin/env python

from setuptools import setup, find_packages
from distutils.core import Extension
import sys
if sys.version_info[0] < 3:
    avro = 'avro'
else:
    avro = 'avro-python3'

module = Extension('confluent_kafka.cimpl',
                   libraries=['rdkafka'],
                   sources=['confluent_kafka/src/confluent_kafka.c',
                            'confluent_kafka/src/Producer.c',
                            'confluent_kafka/src/Consumer.c'])

setup(name='mapr-streams-python',
      version='0.11.0',
      description='MapR Streams Python Client',
      author='Confluent Inc & MapR',
      author_email='support@mapr.com',
      url='https://github.com/mapr/private-kafka-python',
      ext_modules=[module],
      packages=find_packages(exclude=("tests",)),
      data_files=[('', ['LICENSE'])],
      extras_require={
          'avro': ['fastavro', 'requests', avro]
      })