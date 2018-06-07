from setuptools import setup

import configparser

config = configparser.ConfigParser()
config.read('kunteksto.conf')
VERSION = config['SYSTEM']['version']

setup(
    name = 'kunteksto',
    version = VERSION,
    description = 'The Context tool for your data. This is your tool to translate your CSV data files into RDF, XML and JSON with full semantics.',
    long_description = """**Kunteksto** (ˈkänˌteksto) is a tool to help domain experts, data scientists, data creators and data users translate their simple CSV formatted data files 
into the semantically enhanced formats that provide computable metadata. 
    
This automated processing speeds up data cleaning issues and provides a path for existing data to be used in conjunction with the semantic graph approach in the analysis, 
general artificial intelligence and decision support systems. 
    
This translation opens the door for the change to a *datacentric* world of information management. 
    
This new approach enables automatic interoperability avoiding the data quality issues created through data cleaning and massaging. The data is automatically validated according to the constraints that you enter. Invalid data is marked-up to be used as you see fit in your analysis. 
    
The importance of this capability and improved data quality is discussed in foundational `S3Model <https://datainsights.tech/S3Model>`_ documentation and references. However, detailed understanding of S3Model is not required to understand and use the power of Kunteksto. 
The next step for enterprise environments is creating reusable components with the `Datacentric Tool Suite <https://datainsights.tech/datacentrictools/>`_
    
Kunteksto can automatically persist your results data on the file system or in a variety of databases such as:
    
    - AllgeroGraphDB
    - BaseXDB
    - eXistDB (coming in 1.7.0)
    - MongoDB (coming in 1.7.0)
    - MarkLogic (coming in 1.7.0)
    - others? put in a request via the Github Project Issues tab

    """,
    author = 'Timothy W. Cook',
    author_email = 'tim@datainsights.tech',
    url = 'https://datainsights.tech/',  
    download_url = 'https://github.com/DataInsightsInc/Kunteksto/archive/' + VERSION + '.tar.gz',  
    keywords = ['context rdf xml machine learning data-centric semantic interoperability semantics'], 
    tests_require=['pytest',],  
    setup_requires=['pytest-runner',],  
    python_requires='>=3.6',
    packages=['kunteksto'],
    package_dir={'kunteksto': 'kunteksto'},
    package_data={'docs': ['docs/*']},
    data_files=[('example_data', ['example_data/Demo.csv','example_data/Demo2.csv','example_data/Demo3.csv','example_data/Demo_info.pdf','example_data/honeyproduction.csv']),
                ('s3model', ['s3model/s3model_3_1_0.xsl','s3model/s3model_3_1_0.xsd','s3model/s3model_3_1_0.rdf','s3model/s3model.owl','s3model/dm-description.xsl']),
                ('output', ['output/dm-description.xsl']),('catalogs',['catalogs/Kunteksto_catalog.xml']),('',['kunteksto.conf','README.md','LICENSE.txt']),('utils',['utils/datastats.py','utils/db_setup.py'])],
    install_requires=[
        'agraph-python',
        'basexclient',
        'click',
        'lxml',
        'shortuuid',
        'sphinx',
        'sphinx-rtd-theme',
        'ujson',
        'xmltodict',
        'cuid'
      ],
    entry_points='''
            [console_scripts]
            kunteksto=kunteksto.kunteksto:main
        ''',    
    classifiers = ['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Customer Service',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Education',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Financial and Insurance Industry',
                   'Intended Audience :: Healthcare Industry',
                   'Intended Audience :: Information Technology',
                   'Intended Audience :: Legal Industry',
                   'Intended Audience :: Manufacturing',
                   'Intended Audience :: Other Audience',
                   'Intended Audience :: Religion',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: System Administrators',
                   'Intended Audience :: Telecommunications Industry',
                   'License :: OSI Approved :: Apache Software License',
                   'Programming Language :: Python :: 3 :: Only',
                   'Topic :: Scientific/Engineering :: Information Analysis',
                   ],

)