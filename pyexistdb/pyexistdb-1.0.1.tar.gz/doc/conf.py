# pyexistdb documentation build configuration file

import pyexistdb
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = os.path.join(os.path.basename(__file__), 'doc_djangosettings.py')
sys.path.insert(0, os.path.abspath('..'))
from django.conf import settings
settings.configure()

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx']

#templates_path = ['templates']
exclude_trees = ['build']
source_suffix = '.rst'
master_doc = 'index'

project = 'pyexistdb'
copyright = '2017, The Research Software Company'
version = '%d.%d' % pyexistdb.__version_info__[:2]
release = pyexistdb.__version__
modindex_common_prefix = ['pyexistdb.']

pygments_style = 'sphinx'

html_style = 'default.css'
#html_static_path = ['static']
htmlhelp_basename = 'pyexistdbdoc'

latex_documents = [
  ('index', 'pyexistdb.tex', 'pyexistdb Documentation',
   'The Research Software Company', 'manual'),
]

# configuration for intersphinx: refer to the Python standard library, eulxml, django
intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
    'django': ('http://django.readthedocs.org/en/latest/', None),
    'eulxml': ('http://eulxml.readthedocs.org/en/latest/', None),
}
