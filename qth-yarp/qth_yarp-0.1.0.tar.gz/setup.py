from setuptools import setup, find_packages

with open("qth_yarp/version.py", "r") as f:
    exec(f.read())

setup(
    name="qth_yarp",
    version=__version__,
    packages=find_packages(),

    # Metadata for PyPi
    url="https://github.com/mossblaser/qth_yarp",
    author="Jonathan Heathcote",
    description="Library for writing reactive programming style scripts with Qth.",
    license="GPLv2",
    classifiers=[
        "Development Status :: 3 - Alpha",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",

        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    keywords="mqtt asyncio home-automation messaging home automation yarp reactive",

    # Requirements
    install_requires=["qth>=0.6.0", "yarp>=0.1"],
)
