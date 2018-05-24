from setuptools import setup
from setuptools import find_packages


setup(name='phonetic_algorithmRu',
     version='0.10.1',
     description='Phonenetic algorithm for Russian language',
     author='Anastasiya Kostyanitsyna, George Moroz',
     packages=find_packages(),
     include_package_data=True,
     install_requires=['numpy==1.14.2', 'pandas==0.22.0'],
     zip_safe=False
)
