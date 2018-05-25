from setuptools import setup, find_packages

setup(
    name='emulator',
    version='1.7',
    description='Python-Flask application to emulate IoT devices',
    author='FutureHome',
    author_email='fh@futurehome.no',
    packages=find_packages(),
    include_package_data=True,
    package_data = {
        'emulator': ['emulator/static/prop_files/*.json']
    },
    install_requires=[
        'flask',
    ],
    url='https://github.com/futurehomeno/Emulator',

)
