try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
'description': 'Convert alphanumeric text to morse',
'author': 'Shashank Singh',
'url': 'http://www.github.com/shashank9830',
'download_url': 'http://www.github.com/shashank9830',
'author_email': 'shashank9830@gmail.com',
'version': '0.1',
'install_requires': ['nose'],
'py_modules': ['morsify'],
'name': 'morsify'
}

setup(**config)
