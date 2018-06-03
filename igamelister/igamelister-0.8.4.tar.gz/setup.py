from setuptools import setup, find_packages


def readme():
    with open("README.md", "r") as fh:
        return fh.read()


setup(
    name="igamelister",
    version="0.8.4",
    author="Chris Van Graas",
    author_email="cvgcode@gmail.com",
    description="A tool to generate nicely formatted gameslist and genre files for iGame, an AmigaOS WHDLoad launcher "
                "application.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/chris-vg/igamelister",
    packages=find_packages(),
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    include_package_data=True,
    install_requires=[
        "Click",
        "coloredlogs",
        "lhafile",
        "lxml",
        "requests",
        "progressbar2",
    ],
    entry_points="""
        [console_scripts]
        igamelister=igamelister.__main__:cli
    """,
)
