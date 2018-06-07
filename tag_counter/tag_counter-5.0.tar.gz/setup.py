from setuptools import setup, find_packages
import tag_counter
from os.path import join, dirname

setup(
    name='tag_counter',
    version=tag_counter.__version__,
    packages=find_packages(),
    include_package_data=True,
    # long_description=open(join(dirname(__file__), 'README.md')).read(),
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'tag_counter = tag_counter.core:print_message',
            'serve = tag_counter.web:run_server',
        ]
    },
    install_requires=[
    'Flask==0.8'
    ]
)
