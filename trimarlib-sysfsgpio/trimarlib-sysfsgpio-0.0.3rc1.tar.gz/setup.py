import setuptools


with open('./sysfsgpio/version.py') as fd:
    exec(fd.read())

with open("README.md", "r") as fd:
    long_description = fd.read()

setuptools.setup(
    name="trimarlib-sysfsgpio",
    version=VERSION,
    author="Kacper Kubkowski",
    author_email="developer@trimar.com.pl",
    description="Sysfs GPIO utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://dsl2.trimar.org/pythons/sysfsgpio",
    packages=['sysfsgpio'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ),
)
