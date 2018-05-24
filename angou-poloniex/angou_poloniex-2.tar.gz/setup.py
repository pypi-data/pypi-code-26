from setuptools import setup


VERSION = '2'


setup(name='angou_poloniex',
      version=VERSION,
      description='Lightweight and suckless Poloniex REST API client library',
      url='http://github.com/angou-exchange-utils/angou-poloniex',
      download_url='https://github.com/angou-exchange-utils/angou-poloniex/tarball/v' + VERSION,
      author='shdown',
      author_email='shdownnine@gmail.com',
      license='LGPLv3',
      packages=['angou_poloniex'],
      install_requires=['requests'],
      python_requires='>=3',
      platforms=['any'],
      keywords='angou poloniex crypto exchange',
      classifiers=[
          'Development Status :: 1 - Planning',
          'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Internet',
          'Topic :: Software Development :: Libraries',
      ],
      zip_safe=False)
