from setuptools import setup
setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='tree-file-repo',
    url='https://github.com/agencianacionaldigital/3-file-repo',
    author='Agencia Nacional Digital',
    author_email='agencianacionaldigital@and.gov.co',
    # Needed to actually package something
    packages=['filerepo'],
    # Needed for dependencies
    #install_requires=['numpy'],
    # *strongly* suggested for sharing
    version='0.2.2',
    # The license can be anything you like
    license='MIT',
    description='3-file-repo is a python package for saving files in a tree-folder-structure way',
    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
)