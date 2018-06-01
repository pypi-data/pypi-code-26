from setuptools import setup


setup(
    name='cosmic-ray-localpool',
    version='1.0.1',
    packages=['localpool'],
    entry_points={
        'cosmic_ray.execution_engines': [
            'localpool = localpool.executor:LocalPoolExecutionEngine',
        ]
    },
    python_requires='>=3.6.0'
)
