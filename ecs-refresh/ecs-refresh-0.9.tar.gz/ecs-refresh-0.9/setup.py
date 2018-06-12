from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='ecs-refresh',
      version='0.9',
      description='Small tool to kick off ECS blue/green deployments',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Systems Administration',
      ],
      url='http://github.com/PlethoraOfHate/ecs-refresh',
      download_url='https://github.com/PlethoraOfHate/ecs-refrech/archive/0.9.tar.gz',
      author='Stephen Mercier',
      author_email='stephen.mercier@gmail.com',
      license='Apache License 2.0',
      keywords=['ECS', 'AWS'],
      packages=[],
      install_requires=[
        "click",
        "boto3",
      ],
      include_package_data=True,
      zip_safe=False,
      scripts=['scripts/ecs-refresh']
      )