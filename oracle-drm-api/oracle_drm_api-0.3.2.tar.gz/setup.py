import setuptools

def readme():
    with open("README.md", "r") as fh:
        return fh.read()

setuptools.setup(
    name="oracle_drm_api",
    version="0.3.2",
    author="Keith Kikta",
    author_email="keith.kikta@tevpro.com",
    description="Oracle Data Relationship Management API Client",
    long_description=readme(),
    url="https://github.com/tevpro/drm_api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'enum34;python_version<"3.4"',
        'zeep == "2.5.0"'
    ]
)
