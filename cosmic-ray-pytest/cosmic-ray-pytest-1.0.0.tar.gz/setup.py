from setuptools import setup


setup(
    name='cosmic-ray-pytest',
    version='1.0.0',
    packages=['cosmic_ray_pytest'],
    url='https://gitlab.com/pv.zarubin/cosmic_ray_plugins',
    entry_points={
        'cosmic_ray.test_runners': [
            'pytest = cosmic_ray_pytest.runner:PytestRunner',
        ]
    },
    python_requires='>=3.6.0'
)
