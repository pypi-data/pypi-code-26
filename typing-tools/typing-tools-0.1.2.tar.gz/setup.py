from distutils.core import setup

# Fails to upload *valid* markdown description with the following error:
# HTTPError: 400 Client Error: The description failed to render in the default format of reStructuredText.
# See https://pypi.org/help/#description-content-type for more information. for url: https://upload.pypi.org/legacy/ 
with open("README.pypi.md", "r") as fh:
    long_description = fh.read()

setup \
(
    name='typing-tools',
    version='0.1.2',
    packages=[ 'typing_tools' ],
    url='https://gitlab.com/Hares/typing-tools',
    license='MIT',
    author='Peter Zaitcev / USSX Hares',
    author_email='ussx-hares@yandex.ru',
    description='Provides tools for typing in Python 3.6',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
