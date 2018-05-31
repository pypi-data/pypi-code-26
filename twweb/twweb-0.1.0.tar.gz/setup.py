import os

from setuptools import setup, find_packages

basepath = os.path.dirname(__file__)


def main():
    install_reqs = ['Flask==1.0.2',
                    'flask-login==0.4.1',
                    'flask-sqlalchemy==2.3.1',
                    'flask-wtf==0.14.2',
                    'passlib==1.7.1',
                    'taskw==1.2.0']

    setup(name='twweb',
          description='Taskwarrior Web View',
          use_scm_version={'write_to': '.version.txt'},
          license='GPLv3+',
          author='Michał Góral',
          author_email='dev@mgoral.org',
          url='',
          platforms=['linux'],
          setup_requires=['setuptools_scm', 'babel'],
          install_requires=install_reqs,

          # https://pypi.python.org/pypi?%3Aaction=list_classifiers
          classifiers=['Development Status :: 1 - Planning',
                       'Environment :: X11 Applications',
                       'Intended Audience :: End Users/Desktop',
                       'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                       'Natural Language :: English',
                       'Operating System :: POSIX',
                       'Programming Language :: Python :: 3 :: Only',
                       'Programming Language :: Python :: 3.5',
                       'Programming Language :: Python :: 3.6',
                       'Topic :: Internet'],

          packages=find_packages('src'),
          package_dir={'': 'src'},
    )


if __name__ == '__main__':
    main()
