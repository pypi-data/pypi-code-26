import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="anonphoto",
    version="1.0.3",
    author="TurkishTinMan",
    author_email="riccardo.salladini@gmail.com",
    description="Automated anonymizer photo (face & plate)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TurkishTinMan/anonymize-photo",
    license='MIT',
    install_requires=[
	  'face_recognition',
    ],

)