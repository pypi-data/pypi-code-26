import setuptools

VERSION = '0.0.9'

INSTALL_REQUIRES = [
  'cycler>=0.10.0',
  'decorator>=4.0.11',
  'matplotlib>=2.0.0',
  'networkx>=1.11',
  'numpy>=1.14.0',
  'pandas>=9.0.1',
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
        classifiers=(
                    "Programming Language :: Python :: 3",
                    "License :: OSI Approved :: Apache Software License",
                    "Operating System :: OS Independent",
                    ),
    install_requires=INSTALL_REQUIRES
    )

