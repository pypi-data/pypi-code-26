import setuptools

try:
    import pypandoc
    long_description = pypandoc.convert('readme.md', 'rst')
except(IOError, ImportError):
    long_description = open('readme.md').read()

setuptools.setup(name='PyTlin',
      description = 'Kotlin functions also, let, and run, as well as sh-like (and Mathematica-like) piping syntax',
      long_description = long_description,
      long_description_content_type = 'text/markdown',
      url = 'https://github.com/frejonb/PyTlin',
      author = 'F. G. Rejon Barrera',
      author_email = 'f.g.rejonbarrera@gmail.com',
      license = 'MIT',
      version='1.2',
      py_modules=['PyTlin'],
      classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ),
    )
