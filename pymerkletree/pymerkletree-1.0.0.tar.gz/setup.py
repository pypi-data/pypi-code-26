from setuptools import find_packages
from setuptools import setup

install_requires = [
    "pysha3>=1.0b1"
]

setup(
    name='pymerkletree',
    version='1.0.0',
    description='Simple Merkle Tree',
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    url='https://github.com/aliciawyy/pymerkletools',
    author='Alice Wang, Eder Santana',
    keywords='merkle tree, blockchain',
    license="MIT",
    packages=find_packages(),
    include_package_data=False,
    zip_safe=False,
    install_requires=install_requires
)
