from setuptools import setup


with open("../README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='cosmic-ray-pytest',
    version='1.0.1',
    packages=['cosmic_ray_pytest'],
    entry_points={
        'cosmic_ray.test_runners': [
            'pytest = cosmic_ray_pytest.runner:PytestRunner',
        ]
    },
    python_requires='>=3.6.0',
    author="Sixty North AS",
    url='https://gitlab.com/pv.zarubin/cosmic_ray_plugins',
    license='MIT License',
    description="Pytest test-runner plugin for Cosmic Ray.",
    long_description=long_description,
    long_description_content_type="text/markdown"
)
