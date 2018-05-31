from setuptools import setup
from setuptools import find_packages

setup(name="dagraph",
        version="0.1.3",
        description="DAgraph - A directed acyclic graph generation library with integrated optimization",
        author="Rano Veder, Lorenzo Terenzi, Jose Ignacio de Alvear Cardenas",
        license="MIT",
        packages=find_packages(), 
        test_suite='nose.collector',
        tests_require=['nose', 'nose-cover3'])