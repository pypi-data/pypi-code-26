from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup (
	name = "twokenize",
	packages = ["twokenize"],
	version = "1.0.0",
	description = "Word segmentation / tokenization focussed on Twitter",
	author = "Richard Townsend",
	author_email = "richard@sentimentron.co.uk",
	keywords = ["tokenizer"],
	url='https://github.com/Sentimentron/ark-twokenize-py',
	classifiers = [
		"Programming Language :: Python",
		"Programming Language :: Python :: 3",
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Environment :: Console"
	],
	license='GPLv3',
	long_description=long_description,
    long_description_content_type="text/markdown"
)
