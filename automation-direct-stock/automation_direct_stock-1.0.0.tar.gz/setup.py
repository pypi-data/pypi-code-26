import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="automation_direct_stock",
    version="1.0.0",
    author="Philip Conte",
    author_email="philipmconte@gmail.com",
    description="package checks Automation Direct's products' availability",
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url = 'https://github.com/PhilipConte/automation_direct_stock/archive/1.0.0.tar.gz',
    url="https://github.com/PhilipConte/automation_direct_stock",
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
    ],
    scripts=['bin/adstock'],
    keywords='automation direct stock',
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)