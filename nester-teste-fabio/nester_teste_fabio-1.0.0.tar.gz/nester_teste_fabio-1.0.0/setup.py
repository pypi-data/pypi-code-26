from setuptools import find_packages, setup

setup(
    name='nester_teste_fabio',
    packages=find_packages(),
    version='1.0.0',
    description='Descrição curta do meu pacote',
    long_description='Longa descrição do meu pacote',
    author='Fabio Rezende',
    author_email='rezendefabio@gmail.com',
    url='https://github.com/rezendefabio/nester',
    install_requires=['dependencia1', 'dependencia2'],
    license="MIT",
    keywords=['dev', 'web'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
