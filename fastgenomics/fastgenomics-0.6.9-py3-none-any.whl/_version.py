"""
A version helper in the spirit of versioneer.

Minimalistic and able to run without build step using pkg_resources.
"""

import re
import os
from pathlib import Path
from subprocess import run, PIPE, CalledProcessError
from typing import NamedTuple, List


RE_VERSION = r'([\d.]+?)(?:\.dev(\d+))?(?:\+([0-9a-zA-Z.]+))?'
RE_GIT_DESCRIBE = r'v?([\d.]+)-(\d+)-g([0-9a-f]{7})(-dirty)?'
ON_RTD = os.environ.get('READTHEDOCS') == 'True'


def match_groups(regex, target):
    match = re.match(regex, target)
    if match is None:
        raise re.error(f'Regex does not match “{target}”. RE Pattern: {regex}', regex)
    return match.groups()


class Version(NamedTuple):
    release: str
    dev: str
    labels: List[str]
    
    @staticmethod
    def parse(ver):
        release, dev, labels = match_groups(f'{RE_VERSION}$', ver)
        return Version(release, dev, labels.split('.') if labels else [])
    
    def __str__(self):
        dev = f'.dev{self.dev}' if self.dev else ''
        labels = f'+{".".join(self.labels)}' if self.labels else ''
        return f'{self.release}{dev}{labels}'


def get_version_from_dirname(name, parent):
    """Extracted sdist"""
    parent = parent.resolve()
    
    if not re.match(f'{name}-{RE_VERSION}$', parent.name):
        return None
    
    return Version.parse(parent.name[len(name)+1:])


def get_version_from_git(parent):
    parent = parent.resolve()
    
    try:
        p = run(['git', 'rev-parse', '--show-toplevel'], cwd=parent, stdout=PIPE, stderr=PIPE, encoding='utf-8', check=True)
    except (OSError, CalledProcessError):
        return None
    if Path(p.stdout.rstrip('\r\n')).resolve() != parent.resolve():
        # The top-level directory of the current Git repository is not the same
        # as the root directory of the distribution: do not extract the version from Git.
        return None
    
    p = run(
        [
            'git', 'describe',
            '--tags', '--dirty', '--always', '--long',
            '--match', 'v[0-9]*',
        ],
        cwd=parent, stdout=PIPE, stderr=PIPE, encoding='utf-8', check=True,
    )
    
    release, dev, hex, dirty = match_groups(f'{RE_GIT_DESCRIBE}$', p.stdout.rstrip('\r\n'))
    
    labels = []
    if dev == '0':
        dev = None
    else:
        labels.append(hex)
    
    if dirty and not ON_RTD:
        labels.append('dirty')
    
    return Version(release, dev, labels)


def get_version_from_metadata(name, parent):
    try:
        from pkg_resources import get_distribution, DistributionNotFound
    except ImportError:
        return None
    
    try:
        pkg = get_distribution(name)
    except DistributionNotFound:
        return None
    
    # For an installed package, the parent is the install location
    if Path(pkg.location).resolve() == parent.resolve():
        return None
    
    return Version.parse(pkg.version)


def get_version(path):
    """Path: module path (…/module.py or …/module/__init__.py)"""
    path = Path(path)
    assert path.suffix == '.py'
    if path.name == '__init__.py':
        name = path.parent.name
        parent = path.parent.parent
    else:
        name = path.with_suffix('').name
        parent = path.parent
    
    return str(
        get_version_from_dirname(name, parent) or
        get_version_from_git(parent) or
        get_version_from_metadata(name, parent)
    )


if __name__ == '__main__':
    fake_path = Path(__file__).parent / '__init__.py'
    print(get_version(fake_path))
