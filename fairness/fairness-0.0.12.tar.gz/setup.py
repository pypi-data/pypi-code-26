import setuptools

VERSION = '0.0.12'

INSTALL_REQUIRES = [
  'pandas>=0.21.1',
  'pyparsing>=2.1.4',
  'python-dateutil>=2.6.0',
  'pytz',
  'readline>=6.2',
  'scikit-learn>=0.18.1',
  'scipy>=0.19.0',
  'six>=1.10.0',
  'wheel>=0.29.0',
  'fire',
  'BlackBoxAuditing>=0.1.26'
  'ggplot'
]

PACKAGE_DATA = {
  'fairness' : ['data/raw/*.csv','data/preprocessed/*.csv']
}

with open("README.md", "r") as fh:
    long_description = fh.read()

    setuptools.setup(
    name="fairness",
    version=VERSION,
    author="See Authors.txt",
    author_email="fairness@haverford.edu",
    description="Fairness-aware machine learning: algorithms, comparisons, bechmarking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/algofairness/fairness-comparison",
    packages=setuptools.find_packages(),
    package_data = PACKAGE_DATA,
    classifiers=(
                 "Programming Language :: Python :: 3",
                 "License :: OSI Approved :: Apache Software License",
                 "Operating System :: OS Independent",
                ),
    install_requires=INSTALL_REQUIRES
    )

