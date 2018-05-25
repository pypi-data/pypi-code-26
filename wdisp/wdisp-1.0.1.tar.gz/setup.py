
from setuptools import setup

long_description = "An imshow showing the images in a browser."
	
setup(
    name = "wdisp",
    version = "1.0.1",
    description = "imshow for a browser",
    long_description = long_description, 

    url = "https://github.com/mgb4/wdisp",
    author = "Michael Burisch",
    author_email = "michael.burisch@gmx.com",
    
    keywords = "imshow browser",

    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ],
    
    packages = ["wdisp"],

    package_data = {
        "": ["wwwroot/*.*"]
    },


    python_requires = ">=3.4",
	
    install_requires = ["numpy"],
    extras_require = {
        "Server": ["aiohttp"]
    }
)