from setuptools import setup, find_packages

setup(
    name='pybdsim',
    version='1.6',
    packages=find_packages(exclude=["docs", "tests", "obsolete"]),
    # Not sure how strict these need to be...
    install_requires=["matplotlib",
                      "numpy",
                      "scipy",
                      "fortranformat",
                      "root-numpy",
                      "pymadx",
                      "pymad8"],
    # Some version of python2.7
    python_requires="==2.7.*",

    author='JAI@RHUL',
    author_email='laurie.nevay@rhul.ac.uk',
    description=("Python utilities for the Monte Carlo"
                 " Particle accelerator code BDSIM."),
    license="GPL3",
    url='https://bitbucket.org/jairhul/pybdsim/'
)
