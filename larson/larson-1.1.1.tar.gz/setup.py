from setuptools import setup

DEPENDENCIES = ['boto3>=1.5.0,<2.0.0', 'fire>=0.1.0,<0.2.0']

setup(
    name='larson',
    version='1.1.1',
    description='Library for managing secrets',
    url='https://projects.pbs.org/bitbucket/users/cmacdonald/repos/larson/browse',
    author='Chris MacDonald',
    author_email='cmacdonald@pbs.org',
    packages=['larson'],
    scripts=['bin/larson', 'bin/larson_json_to_vars'],
    zip_safe=False,
    install_requires=DEPENDENCIES,
    python_requires='>=3.3'
)
