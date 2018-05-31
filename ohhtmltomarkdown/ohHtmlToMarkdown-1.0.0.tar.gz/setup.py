import setuptools

with open('README.md', 'r',encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="ohHtmlToMarkdown",
    version="1.0.0",
    description="A Python Library for converting HTML to Markdown.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ethan Huang",
    author_email="wfgydbu@163.com",
    url='https://github.com/wfgydbu/ohHTML2Markdown',
    packages=setuptools.find_packages(),
    license='GNU GPL 3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 3.6',
        "Operating System :: OS Independent"
    ],
    install_requires=['beautifulsoup4==4.6.0'],
    py_modules=['ohHtmlToMarkdown'],
    include_package_data=True,
    zip_safe=False,
)