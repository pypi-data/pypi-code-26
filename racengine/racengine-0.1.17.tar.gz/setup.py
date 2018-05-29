# import os
from setuptools import setup
# from setuptools import find_packages
# from pip.req import parse_requirements


# setup_dir = os.path.dirname(os.path.realpath(__file__))
# path_req = os.path.join(setup_dir, 'requirements.txt')
# install_reqs = parse_requirements(path_req, session=False)

# reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='racengine',
    version='0.1.17',
    description='Generate Docx from template (using external api endpoint) '
                'and convert it to PDF or another format(using external api endpoint)',
    author='SFERENO SAS',
    author_email='adminsys@sfereno.com',
    packages=['racengine'],
    install_requires=["requests == 2.18"],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers'
    ]
)