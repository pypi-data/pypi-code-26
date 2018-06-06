from setuptools import setup , find_packages


install_requires = [
    'setuptools',
    'Django >= 2.0.2',
    'Pillow >= 2.2.2'
]

setup(
    name="captcha-varis-main",
    version='1.0',
    url='https://github.com/varisbhalala/captcha-simple.git',
    install_requires=install_requires,
    licence='MIT',
    packages=find_packages(),
    include_package_data=True,
)