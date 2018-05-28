from setuptools import setup

setup(name="koicore",
      version="1.0.2",
      description="The core library for Koi written in Python.",
      author="koi-lang",
      url="https://github.com/koi-lang/koi-python",
      license="BSD 3-Clause",
      classifiers=[
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
      ],
      keywords=["koi", "core", "language", "interpreter", "compiler"],
      packages=["koicore", "koicore/other", "koicore/types"])
