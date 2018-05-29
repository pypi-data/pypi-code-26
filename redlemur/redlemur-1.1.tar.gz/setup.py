from distutils.core import setup
setup(
  name = 'redlemur',
  packages = ['lemur', 'lemur.utils'],
  version = '1.1',
  description = 'High level visualization library',
  author = 'Nitin Kumar',
  author_email = 'nkumar14@jhu.edu',
  url = 'https://github.com/NeuroDataDesign/lemur',
  download_url = 'https://github.com/NeuroDataDesign/lemur/archive/1.0.tar.gz',
  keywords = ['visualization', 'neuroscience', 'embeddings'],
  install_requires = [
    'scipy==1.0.0',
    'matplotlib==2.1.0',
    'plotly==2.2.2',
    'seaborn==0.8.1',
    'ipywidgets==7.0.5',
    'pandas==0.21.0',
    'numpy==1.13.3',
    'colorlover==0.2.1',
    'scikit_learn==0.19.1',
    'nilearn==0.4.0',
    'nibabel==2.2.1',
    'imageio==2.2.0',
    'networkx==2.1'
  ],
  classifiers = [],
)
