from setuptools import setup

setup(
    name='gais_json_convertor',
    version = '0.0.4',
    description = 'Convertor for GAIS format and JSON format.',
    long_description = open('docs/README.txt', 'r', encoding='utf-8', errors='replace').read(),
    author = 'Szu-Hsuan, Wu',
    author_email = 'shuan0713@gmail.com',
    url = 'https://github.com/wshs0713/gais_json_convertor.git',
    packages = ['gais_json_convertor'],
    keywords = ['GAIS', 'JSON', 'gais_json_convertor'],
    license = 'docs/LICENSE.txt',
    install_requires=[
    ]
)