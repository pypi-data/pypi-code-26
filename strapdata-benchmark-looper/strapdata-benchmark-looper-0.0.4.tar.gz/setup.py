import setuptools

setuptools.setup(
    name="strapdata-benchmark-looper",
    version="0.0.4",
    author="Barthelemy Delemotte",
    author_email="barth@strapdata.com",
    description="Run elassandra benchmark",
    packages=[],
    install_requires=['PyYAML'],
    scripts=['./benchmark-looper.py'],
    data_files=[('/etc/benchmark-looper', ['docker-compose.yml', 'todo-example.json'])]
)
