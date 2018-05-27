from setuptools import setup

setup(
    name="provbug",
    packages=["provbug"],
    version="0.2.1",    
    scripts=['provbug/provbug.py', 'provbug/FunctionActivation.py', 'provbug/VariableState.py'],
    entry_points={
        "console_scripts": ["provbug=provbug:main"]
    },
    author=("Henrique Linhares, and Rômulo Ponciano"),
    author_email="hlinhares@id.uff.br",
    description="Supporting infrastructure to debug scientific experiments with noworkflow",
    keywords=["scientific", "experiments", "provenance", "debug"],
    url="https://github.com/linharesh/provbug",
    python_requires='>=3.5',
    classifiers=[
    	'Development Status :: 3 - Alpha',

    	'License :: OSI Approved :: MIT License',

    	'Programming Language :: Python :: 3.5',
    	'Programming Language :: Python :: 3.6',
    ],
)