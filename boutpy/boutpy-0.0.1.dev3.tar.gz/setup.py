import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="boutpy",
    version="0.0.1.dev3",
    author="J.G. Chen, BOUT++ TEAM",
    author_email="cjgls@pku.edu.cn",
    description="Common python2.x toolkits for BOUT++ project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/conderls/boutpy",
    packages=setuptools.find_packages(),
    python_requires="~=2.7",
    scripts=[
        'boutpy/bin/compare_inp.py',
        'boutpy/bin/gamma.py',
        'boutpy/bin/growthrate.py',
        'boutpy/bin/jobstate.py',
        'boutpy/bin/jobsubmit.py',
        'boutpy/bin/scan.py',
    ],
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    project_urls={
        "Documentation": "https://boutpy.readthedocs.io",
        "Source": "https://gitlab.com/conderls/boutpy",
        "Tracker": "https://gitlab.com/conderls/boutpy/issues",
    },
    install_requires=[
        "numpy >= 1.13.1",
        "scipy",
        "matplotlib >= 2.0.2",
        "pandas >= 0.18.1",    # stack() new usage
        "ipython >= 5.5.0",    # solve PyQt4 Error
        "configobj",
        "netCDF4",
        "future",
    ],
)

