from setuptools import setup, find_packages

version = '0.0.1'
name = 'osm-graph'
short_description = '`osm-graph` is a package for NetworkX and OpenStreetMap.'
long_description = """\
`osm-graph` is a package for NetworkX and OpenStreetMap.
::

   %matplotlib inline
   import networkx as nx
   from osm_graph import OsmGraph
   og = OsmGraph(35.7158, 139.8741)
   nd1 = og.find_node(35.7165, 139.8738)
   nd2 = og.find_node(35.7153, 139.8752)
   path = nx.dijkstra_path(og.graph, nd1, nd2)
   g = nx.subgraph(og.graph, path)
   ax = og.draw_graph()
   og.draw_graph(graph=g, ax=ax, edge_color='r', width=2);

Requirements
------------
* Python 3, networkx, matplotlib, overpy

Features
--------
* This is a sample. So it may not be efficient.

Setup
-----
::

   $ pip install osm-graph

History
-------
0.0.1 (2018-6-9)
~~~~~~~~~~~~~~~~~~
* first release

"""

classifiers = [
   "Development Status :: 1 - Planning",
   "License :: OSI Approved :: Python Software Foundation License",
   "Programming Language :: Python",
   "Intended Audience :: Developers",
   "Intended Audience :: Science/Research",
   "Topic :: Scientific/Engineering",
   "Topic :: Software Development",
]

setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=classifiers,
    #py_modules=['osm-graph'],
    packages=find_packages(),
    keywords=['osm-graph',],
    author='Saito Tsutomu',
    author_email='tsutomu.saito@beproud.jp',
    url='https://pypi.python.org/pypi/osm-graph',
    license='PSFL',
    install_requires=['networkx', 'matplotlib', 'overpy', ],
)
