from setuptools import setup, Extension

allium_hash_module = Extension('allium_hash',
                               sources = [
										  'lyra2re2module.c',
                                          'Lyra2RE.c',
										  'Sponge.c',
										  'Lyra2.c',
										  'sha3/blake.c',
										  'sha3/groestl.c',
										  'sha3/keccak.c',
										  'sha3/cubehash.c',
										  'sha3/bmw.c',
										  'sha3/skein.c'],
                               include_dirs=['.', './sha3'])

setup (name = 'allium_hash',
       version = '1.0.2',
       author_email = 'ryan@rshaw.me',
       author = 'Ryan Shaw',
       url = 'https://github.com/ryan-shaw/allium-hash-python',
       description = 'Bindings for Allium proof of work used by Garlicoin',
       ext_modules = [allium_hash_module])

