import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

    setuptools.setup(
    name="fairness",
    version="0.0.5",
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
    )
