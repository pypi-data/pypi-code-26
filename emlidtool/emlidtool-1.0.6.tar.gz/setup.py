from setuptools import setup, find_packages


print(find_packages())
setup(
    name="emlidtool",
    version="1.0.6",
    license="GPL",
    author="Georgii Staroselskii",
    author_email="georgii.staroselskii@emlid.com",
    url="https://github.com/emlid/emlidtool",
    packages=find_packages(),
    # should be passed as arguments also
    # we don't list systemwide installed packages like smbus and spidev as pip seems to be not smart enough to
    # resolve these dependencies
    install_requires=[
	"coloredlogs==6.0",
	"navio2==1.0.0",
	"appdirs==1.4.3",
	"cffi==1.10.0",
	"coloredlogs==6.0",
	"coverage==4.4",
	"humanfriendly==2.4",
	"packaging==16.8",
	"pbr==3.1.1",
	"py==1.4.33",
	"pycparser==2.17",
	"pyparsing==2.2.0",
	"six==1.10.0",
	"smbus-cffi==0.5.1",
	"spidev==3.2",
	"termcolor==1.1.0",
	"urwid==1.3.1",
        "progressbar2==3.34.3"
    ],
    entry_points={
        "console_scripts": [
            "emlidtool= emlid.emlidtool:main"
            ]
    }
)
