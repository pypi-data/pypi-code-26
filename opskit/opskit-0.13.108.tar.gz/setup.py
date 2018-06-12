from distutils.core import setup
setup(
  name = 'opskit',
  py_modules = ['opskitcl'],
  packages = ['opskit'], 
  entry_points = {
    'console_scripts': ['opskit=opskitcl:main'],
  },
  description = 'OpsKit is a plugin-based command line to for simplified organization of dev-ops scripts into a single tool',
  version = '0.13.108',
  author = 'Mark Sweat',
  author_email = 'mark@surfkansas.com',
  url = 'https://github.com/surfkansas/opskit', 
  download_url = 'https://github.com/surfkansas/opskit/archive/0.12.108.tar.gz'
)
