from distutils.core import setup

setup(
    name="analyst",
    packages=[
        "analyst",
        "analyst.viz",
        "analyst.utils",
        
    ],
    version="00.01",
    url="https://github.com/shen-h",

    author="Shen Han",
    author_email="hs@uchicago.edu",

    description="Data analysis toolkit",
    long_description="""\
        Analytical toolkit for data science and machine learning
        --------------------------------------------------------

        Utilities:
         - `ml`: machine learning
         - `nd`: NumPy and Pandas
         - `viz`: data visualization
    """,

    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or "
            "later (LGPLv3+)",
        "Operating System :: OS Independent",

        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Utilities",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Visualization",        
    ]
)
