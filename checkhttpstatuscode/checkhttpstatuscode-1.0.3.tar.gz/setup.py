from setuptools import setup

setup(
    name='checkhttpstatuscode',
    version='1.0.3',
    py_modules=['CheckHttpStatusCode'],
    url='https://gitlab.com/gregoryjordanm/checkhttpstatus',
    license='MIT',
    author='Jordan Gregory',
    author_email='gregory.jordan.m@gmail.com',
    description='Check the status codes of http servers',
    install_requires=[
        'Click',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        CheckHttpStatusCode=CheckHttpStatusCode:check
    ''',
)
