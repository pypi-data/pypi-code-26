import os

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, "doodledashboard", "__about__.py")) as f:
    exec(f.read(), about)

setup(
    name=about['__name__'],
    version=about['__version__'],
    description="Console display for Doodle-Dashboard.",
    url="https://github.com/SketchingDev/Doodle-Dashboard-Console-Display",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "doodle-dashboard",
        "click"
    ],
    entry_points={
        'doodledashboard.displays': [
            'console=doodledashboard.customdisplay.consoledisplay:ConsoleDisplay'
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.4"
    ],
    python_requires=">=3.4"
)
