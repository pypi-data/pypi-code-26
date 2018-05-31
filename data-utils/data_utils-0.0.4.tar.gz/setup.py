from setuptools import setup

# SEE: `https://packaging.python.org/tutorials/distributing-packages/#setup-args`
# And SEE: `https://python-packaging.readthedocs.io/en/latest/minimal.html`.
setup(
    name="data_utils",
    version="0.0.4",
    description="An assortment of utilities for handling dirty, dirty data.",
    url="https://github.com/raywhite/data-utils",
    author="axdg",
    author_email="axdg@dfant.asia",
    license="UNLICENSED",
    classifiers=[],
    keywords="hof higher-order data utilities",
    packages=["data_utils"], # NOTE: Maybe use;packages=setuptools.find_packages()
    install_requires=["phonenumberslite"],
    python_requires=">=2.6,<=3.0",
    package_date={},
    data_files=[],
    py_modules=[],
    entry_points={},
    console_scripts={},
    scripts=[])
