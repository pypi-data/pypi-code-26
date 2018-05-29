from setuptools import setup, find_packages

setup(
    name="ElectronBonder",
    url="https://github.com/RockefellerArchiveCenter/ElectronBonder",
    description="Project Electron Client Library",
    long_description="""A client library for interacting Project Electron applications via their REST APIs.""",
    author="Rockefeller Archive Center",
    author_email="archive@rockarch.org",
    version="0.3.0",
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires=">=2.7",
    install_requires=[
        "requests",
        "six",
    ],
)
