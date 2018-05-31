from setuptools import setup


setup(
    name='fidding-cli',
    version='0.2',
    description='A python cli project',
    url='https://github.com/fidding/python-cli.git',
    packages=['python_cli'],
    author='fidding',
    author_email='395455856@qq.com',
    license='MIT',
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        fidding-cli=python_cli.script.cli:cli
    ''',
)
