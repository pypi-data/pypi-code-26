import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="moduledk",
    version="0.0.1",    
    author="moduledk",
    author_email="moduledk@example.com",
    description="add func",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ModuledkQuy/test",
    packages=setuptools.find_packages(),    
)
