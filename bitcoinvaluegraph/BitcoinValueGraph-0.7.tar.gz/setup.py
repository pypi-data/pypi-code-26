"""
Bitcoin Value
-------------

Bitcoin Value is a simple script that fetches data about value
of Bitcoin for the past month and presents it in a graph as a
SVG file that can be opened in your default browser.

You can get it by downloading it directly or by typing:

    $ pip install BitcoinValueGraph

After it is installed you can start it by simply typing in your terminal:

    $ bitcoin

"""

from setuptools import setup


setup(name="BitcoinValueGraph",
      version="0.7",
      description="Bitcoin value",
      long_description=__doc__,
      url="https://github.com/Urosh91/Bitcoin-Value",
      author="Uroš Jevremović",
      author_email="jevremovic.uros91@gmail.com",
      packages=["BitcoinValueGraph"],
      install_requires=["pygal"],
      entry_points={
          "console_scripts": ["bitcoin=BitcoinValueGraph.bitcoin_value_graph:main"],
      },
      )

__author__ = "Uroš Jevremović"
