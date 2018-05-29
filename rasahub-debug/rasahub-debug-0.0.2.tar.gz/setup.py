from setuptools import setup, find_packages

install_requires = [
    'rasahub',
    'rasahub-debug-client'
]

tests_requires = [
]

extras_requires = {
    'test': tests_requires
}

setup(name='rasahub-debug',
      version='0.0.2',
      description='Debugging connector for Rasahub',
      url='http://github.com/frommie/rasahub-debug',
      author='Christian Frommert',
      author_email='christian.frommert@gmail.com',
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
      ],
      keywords='rasahub',
      packages=find_packages(exclude=['docs', 'tests']),
      install_requires=install_requires,
      tests_require=tests_requires,
      extras_require=extras_requires,
)
