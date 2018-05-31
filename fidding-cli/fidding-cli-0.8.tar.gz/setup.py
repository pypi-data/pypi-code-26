from setuptools import setup, find_packages


setup(
    name='fidding-cli',
    version='0.8',
    description='A python cli project',
    url='https://github.com/fidding/python-cli.git',
    packages=find_packages(),
    author='fidding',
    author_email='395455856@qq.com',
    license='MIT',
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    # package_dir={'': 'lib'},
    # data_files=[],
    entry_points='''
        [console_scripts]
        fidding-cli=python_cli.script.cli:cli
    ''',
)
