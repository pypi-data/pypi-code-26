from setuptools import setup


setup(
    name="MangaDB",
    version="0.1",
    description="Storage/Retrieval Library for Manga Items",
    author="Zedoax",
    author_email="zedoax@anagrio.net",
    url="https://www.github.com/MangaDB",
    install_requires=[
        'SQLAlchemy',
        'datetime'
    ]
)
