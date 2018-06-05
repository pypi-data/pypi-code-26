from setuptools import setup


with open("../README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='cosmic-ray-localpool',
    version='1.0.4',
    packages=['cosmic_ray_localpool'],
    entry_points={
        'cosmic_ray.execution_engines': [
            'localpool = cosmic_ray_localpool.executor:LocalPoolExecutionEngine',
        ]
    },
    python_requires='>=3.6.0',
    author="Pavel Zarubin",
    url='https://gitlab.com/pv.zarubin/cosmic_ray_plugins',
    license='MIT License',
    description="ProcessPool execution engine plugin for Cosmic Ray.",
    long_description=long_description,
    long_description_content_type="text/markdown"
)
