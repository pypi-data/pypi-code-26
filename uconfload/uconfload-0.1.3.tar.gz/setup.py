from setuptools import setup

setup(name='uconfload',
    version='0.1.3',
    description='Universal config loader for standalone and containerized apps.',
    url='https://github.com/edward2a/uconfload-python',
    author='Eduardo A. Paris Penas',
    author_email='edward2a@gmail.com, epp@realread.me',
    license='Apache License 2.0',
    py_modules=['uconfload'],
    install_requires=[
        'PyYAML'
    ],
    zip_safe=True)
