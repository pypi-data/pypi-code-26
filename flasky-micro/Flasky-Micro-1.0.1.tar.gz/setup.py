from setuptools import setup


setup(
    name="Flasky-Micro",
    version="1.0.1",
    description="Flask Micro Service Framework",
    author="Mathieu Paul",
    author_email="laup.mathieu@gmail.com",
    license="MIT",
    packages=["flasky"],
    install_requires=[
        "Flask",
        "Flask-Classy",
        "PyYAML"
    ],
    zip_safe=False
)
