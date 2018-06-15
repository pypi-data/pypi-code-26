from setuptools import setup, find_packages

setup(
    name="amegaparser",
    version="0.1",
    packages=find_packages(),
    license="GPLv3",
    author="tekulvw",
    description="Converter for (old) AmegaView binary data crash files.",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
    ],
    entry_points={"console_scripts": ["amegaparser=amegaparser.amega_parser:cli"]},
    python_requires=">=3.6,<3.7",
    install_requires=["click"],
)
