from setuptools import setup, find_packages

with open("version.txt", "r") as f:
    version = f.read()
    parts = version.split("-")
    if len(parts) > 1:
        exit("Error: Your git repo is not tagged properly: %s" % version)

    tag = parts[0].lstrip("v")
    print("==> Using tag: %s" % tag)

setup(
    name="backups",
    version=tag,
    description="Database backup utilities",
    long_description="Database backup utilities.",
    author="jpedro",
    author_email="jpedro.barbosa@gmail.com",
    url="https://github.com/jpedro/backups",
    download_url="https://github.com/jpedro/backups/tarball/master",
    keywords="backup mysql",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    packages=find_packages(exclude=["docs", "tests"]),
    install_requires=[
        "MySQL-python==1.2.3rc1",
    ],
    entry_points={
        "console_scripts": [
            "backup-mysql=backups.mysql:main",
            "backup-postgres=backups.postgres:main",
        ],
    },
    scripts=[
        "bin/backup-check",
    ],
)
