from setuptools import setup

setup(name="dagraph",
        version="0.1",
        description="DAgraph",
        author="Rano Veder, Lorenzo Terenzi, Jose Ignacio de Alvear Cardenas",
        license="MIT",
        packages=['dagraph'], 
        test_suite='nose.collector',
        tests_require=['nose', 'nose-cover3'])