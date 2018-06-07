from setuptools import setup
 
setup(
    name='tbsh',    # This is the name of your PyPI-package.
    version='0.2.4',                          # Update the version number for new releases    
    author="Sriharsha Sammeta",
    author_email="sriharsha4444@icloud.com",
    description='The funniest joke in the world',
    url='http://github.com/storborg/funniest',
    license='MIT',
    packages=['tbsh'],    
    install_requires=[
        'jupyter',
    ],
    zip_safe=False
)
