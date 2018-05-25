"""Install amivcrm."""

from setuptools import setup

with open("README.md", "r") as file:
    DESCRIPTION = file.read()

setup(
    name="amivcrm",
    version='0.2.0',
    author='Alexander Dietmüller',
    description="A simple connector to the AMIV SugarCRM",
    long_description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=['amivcrm'],
    install_requires=['suds-jurko>=0.6'],
    url="https://gitlab.ethz.ch/amiv/kontakt/amiv-crm-connector",
)
