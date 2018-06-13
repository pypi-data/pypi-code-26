from setuptools import setup, find_packages


setup(
    name="punk",

    version="3.0.0",

    description="Primitives for Uncovering New Knowledge.",
    long_description="Machine Learning pipeline elements.",

    url="https://github.com/NewKnowledge/punk",

    author="New Knowledge",
    author_email="support@newknowledge.io",

    license="MIT",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",

        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3.6",

        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],

    keywords="TA1 primitive, feature selection, novelty detection",

    packages=find_packages(exclude=['tests', 'd3m', 'examples']),

    install_requires=["numpy", "scikit-learn", "scipy", "pandas", "python-dateutil"],
)
