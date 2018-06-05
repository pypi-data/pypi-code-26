import setuptools

with open("README.md", "rb") as f:
    long_description = f.read().decode("utf-8")
    
setuptools.setup(
    name="psyshort",
    version="0.0.8",
    author="Quit3Simpl3",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/Quit3Simpl3/psyshort",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        )
    )

