from setuptools import setup


setup(
    name='cosmic_ray_localpool',
    version='1.0.0',
    packages=['localpool'],
    entry_points={
        'cosmic_ray.execution_engines': [
            'pool = localpool.executor:LocalPoolExecutionEngine',
        ]
    },
    python_requires='>=3.6.0'
)
