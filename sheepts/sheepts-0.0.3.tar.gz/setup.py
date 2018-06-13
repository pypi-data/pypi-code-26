from setuptools import setup

with open("requirements.txt", "r") as f:
    install_requires = [line.strip() for line in f.readlines()]

setup(
    name="sheepts",
    version="0.0.3",
    description="Light Time Series Toolbox",
    long_description="sheepts is a light time series toolbox.",
    url="https://github.com/aliciawyy/sheep",
    author="Alice Wang",
    author_email="rainingilove@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License"
        ],
    keywords="pandas time-series toolbox",
    packages=["sheepts"],
    install_requires=install_requires,
    extras_require={
        "test": ["pytest==3.6.1", "pytest-cov==2.5.1"]
    }
)
