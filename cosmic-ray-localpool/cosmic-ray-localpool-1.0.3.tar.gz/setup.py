from setuptools import setup


setup(
    name='cosmic-ray-localpool',
    version='1.0.3',
    packages=['cosmic_ray_localpool'],
    url='https://gitlab.com/pv.zarubin/cosmic_ray_plugins',
    entry_points={
        'cosmic_ray.execution_engines': [
            'localpool = cosmic_ray_localpool.executor:LocalPoolExecutionEngine',
        ]
    },
    python_requires='>=3.6.0'
)
