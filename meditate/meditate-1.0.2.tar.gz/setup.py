# Copyright (C) 2018 Yuval Langer
#
# This file is part of Meditate.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Setup file."""

from setuptools import setup


DESCRIPTION = "A command line meditation clock."
LONG_DESCRIPTION = open("README.rst").read()

setup(
    name="meditate",
    license="AGPL-3.0-or-later",
    url="https://gitlab.com/yuvallanger/meditate",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author="Yuval Langer",
    author_email="yuval.langer@gmail.com",
    maintainer="Yuval Langer",
    maintainer_email="yuval.langer@gmail.com",
    version="1.0.2",
    classifiers=[
        "Environment :: Console",
        "Framework :: Trio",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="meditation",
    project_urls={
        "Source": "https://gitlab.com/yuvallanger/meditate",
        "Tracker": "https://gitlab.com/yuvallanger/meditate/issues",
        "BitBucket Mirror": "https://bitbucket.org/yuvallanger/meditate",
        "GitGud Mirror": "https://gitgud.io/yuvallanger/meditate",
        "GitHub Mirror": "https://github.com/yuvallanger/meditate",
    },
    packages=["meditate"],
    entry_points={
        "console_scripts": [
            "meditate=meditate:main",
        ],
    },
    include_package_data=True,
    install_requires=[
        "attrs",
        "docopt",
        "simpleaudio",
        "trio",
    ],
    python_requires="~=3.5",
)
