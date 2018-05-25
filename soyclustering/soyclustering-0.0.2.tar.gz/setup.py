from setuptools import setup, find_packages

setup(
    name="soyclustering",
    version='0.0.2',
    author='Lovit',
    author_email='soy.lovit@gmail.com',
    url='https://github.com/lovit/clustering4docs',
    description="Python library for document clustering",
    long_description="Python library for document clustering",
    install_requires=["scikit-learn>=0.18.0", "numpy>=1.14.2"],
    keywords = ['document clustering', 'clustering labeling'],
    packages=find_packages()
)