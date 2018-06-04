from setuptools import setup

setup(name='wikiid2vec',
      version='0.1.1',
      description='Word2Vec model trained by WIKI Indonesia articles',
      url='http://github.com/xhijack/wiki2vec',
      author='xhijack',
      author_email='xhijack@gmail.com',
      license='MIT',
      packages=['wiki2vec'],
      zip_safe=False,
      install_requires=[
            'tqdm',
            'gensim'
      ]
      )
