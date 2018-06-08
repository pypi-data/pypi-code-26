from distutils.core import setup
setup(
  name = 'bbrc-validator',
  packages = ['bbrc'],
  version = '0.2.0.1',
  description = 'Systematic sanity checks on imaging datasets within an XNAT environment',
  author = 'Greg Operto',
  author_email = 'goperto@barcelonabeta.org',
  url = 'https://gitlab.com/bbrc/xnat/bbrc-validator',
  download_url = 'https://gitlab.com/bbrc/xnat/bbrc-validator/-/archive/v0.2/bbrc-validator-v0.2.tar.gz',
  classifiers = ['Intended Audience :: Science/Research',
      'Intended Audience :: Developers',
      'Topic :: Scientific/Engineering',
      'Operating System :: Unix',
      'Programming Language :: Python :: 2.7' ]
)
