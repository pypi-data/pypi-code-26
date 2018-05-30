import os

from setuptools import find_packages, setup


def get_version():
    basedir = os.path.dirname(__file__)
    with open(os.path.join(basedir, 'rt_dashboard/__init__.py')) as f:
        version_line = next(l for l in f if l.startswith('__version__'))
        return eval(version_line.split('=')[1])
    raise RuntimeError('No version info found.')


setup(
    name='rt-dashboard',
    version=get_version(),
    description=('rt-dashboard provides an embeddable web interface for monitoring '
                 'your redis_tasks queues, jobs, and workers in realtime.'),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    python_requires='>=3.6',
    install_requires=['redis_tasks', 'werkzeug', 'jinja2'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
    ]
)
