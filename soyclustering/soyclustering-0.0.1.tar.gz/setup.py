from setuptools import setup, find_packages

setup(
    name="soyclustering",
    version='0.0.1',
    author='Lovit',
    author_email='soy.lovit@gmail.com',
    url='https://github.com/lovit/clustering4docs',
    description="Python library for document clustering",
    long_description="Python library for document clustering",
    install_requires=["scikit-learn>=0.19.1"],
    keywords = ['document clustering', 'clustering labeling'],
    packages=find_packages()
)