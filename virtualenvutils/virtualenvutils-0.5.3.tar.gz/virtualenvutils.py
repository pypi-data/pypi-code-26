# coding: utf-8

from __future__ import print_function, absolute_import, division, unicode_literals

import sys
import os
import subprocess

from ruamel.std.pathlib import Path


class VirtualEnvUtils(object):
    def __init__(self, args, config):
        self._args = args
        self._config = config
        self._venv_dirs = None
        self._link_dir = Path('/usr/local/bin')

    def alias(self):
        """
        aliases is not such a good idea when dealing with crontab files etc
        starting with 0.4 make a link in self._link_dir (/usr/local/bin) instead
        the alias command still works, but if a target for the alias is found
        to be the destination of a symlink in self._link_dir it is commented out
        """
        aliases = dict()
        # for lb in self.linked_binaries:
        #     print('lb', lb)
        keys = []
        venv_dirs = self.venv_dirs[:]
        for d in venv_dirs[:]:
            # check for configuration file
            conf = d / 'virtualenvutils.conf'
            if not conf.exists():
                continue
            venv_dirs.remove(d)
            # print('conf file', d, file=sys.stderr)
            for line in conf.read_text().splitlines():
                line = line.strip()
                if not line:
                    continue
                # print('line', line, file=sys.stderr)
                if u':' in line:
                    util, full = line.strip().split(u":", 1)
                    full = d / 'bin' / full
                else:
                    util = line
                    full = d / 'bin' / util
                if not full.exists():
                    print('cannot find {}\n  from line {}\  in {}'.format(
                        full, line, conf), file=sys.stderr)
                if util in aliases:
                    print('virtualenvutils name clashes {}\n  {}\n  {}'.format(
                        util,
                        util,
                        aliases[util],
                    ), file=sys.stderr)
                else:
                    aliases[util] = full
                    keys.append(util)
        for d in venv_dirs[:]:
            util = d / 'bin' / (d.stem)
            if not util.exists():
                continue
            venv_dirs.remove(d)
            # print('matching virtualenv name', d, file=sys.stderr)
            if util.name in aliases:
                print('virtualenvutils name clashes {}\n  {}\n  {}'.format(
                    util.name,
                    util,
                    aliases[util.name],
                ), file=sys.stderr)
            else:
                aliases[util.stem] = util
                keys.append(util.stem)
        for d in venv_dirs[:]:
            for util in (d / 'bin').glob('*'):
                if not util.is_file():
                    continue
                for skip in ['activate', 'easy_install', 'python', 'pip', 'wheel']:
                    if util.stem.startswith(skip):
                        break
                else:
                    if d in venv_dirs:  # only first time
                        venv_dirs.remove(d)
                    if util.name.endswith('.so'):
                        continue
                    if util.name.endswith('.pyc'):
                        continue
                    if util.name.endswith('.py'):
                        # can make xyz.py into util xyz, or skip. Yeah, skip
                        continue
                    if util.name in aliases:
                        if self._args.verbose > 0:
                            print('skipping name clashes {}\n  {}\nin favor of\n  {}'.format(
                                util.name,
                                util,
                                aliases[util.name],
                            ), file=sys.stderr)
                    else:
                        aliases[util.name] = util
                        keys.append(util.name)
        assert not venv_dirs
        for k in sorted(keys):
            prefix = '# ' if aliases[k] in self.linked_binaries else ''
            print("{}alias {}='{}'".format(prefix, k, aliases[k]))

    @property
    def venv_dirs(self):

        def test_a_dir(sub_dir):
            if not sub_dir.is_dir():
                return False
            for x in ('bin', 'lib', 'include'):
                sub_sub_dir = sub_dir / x
                if not sub_sub_dir.exists():
                    break
                if not sub_sub_dir.is_dir():
                    break
            else:
                activate = sub_dir / 'bin' / 'activate'
                if activate.exists() and activate.is_file():
                    self._venv_dirs.append(sub_dir)
                    return True
            return False

        if self._venv_dirs is not None:
            return self._venv_dirs
        self._venv_dirs = []
        for d in self._args.dir:
            d = Path(d).expanduser()
            if test_a_dir(d):
                continue
            for sub_dir in d.glob('*'):
                test_a_dir(sub_dir)
        return self._venv_dirs

    def update(self):
        import pkgutil  # NOQA
        import pkg_resources  # NOQA
        # pkg_resources.working_set is what pip relies upon, that is bound to the
        # pip/python that is running
        # print('x', [x for x in pkg_resources.working_set])
        # print('pip', pip.__file__)
        pre = ['--pre'] if self._args.pre else []
        pip_args = ['list', '--outdated', '--format=freeze']
        has_run = False
        for d in self.venv_dirs:
            has_run = True
            pip_cmd = [str(d / 'bin' / 'pip')]
            res = [x.split('==', 1)[0] for x in check_output(
                pip_cmd + pip_args + pre).splitlines()]
            print('update', d, res)
            # NOT WORKING: this gives you the packages from the calling environment
            # for package in pip.get_installed_distributions():
            #     print('package', package)
            #
            # for p in (d / 'lib').glob('python*'):
            #     if p:
            #         break
            # else:
            #     continue  # no lib/python* found
            # pth = [str(p / 'site-packages')]
            # NOT WORKING: does give you only toplevel names and not in original dotted
            #              package form
            # for pkg in pkgutil.iter_modules(path=pth):
            #     continue
            #     if pkg[2]:
            #         print('pkg', pkg[1])
            #
            # NOT WORKING: only gives non-namespace packages
            # for pkg in pkgutil.walk_packages(path=pth):
            #     continue
            #     if pkg[2]:
            #         print('pkg', pkg[1])
            #
            if res:
                print(check_output(pip_cmd + ['install', '-U'] + pre + res))
            self.create_link(d)
        if not has_run:
            print('no project(s) found')

    @property
    def linked_binaries(self):
        attr = '_' + sys._getframe().f_code.co_name
        if not hasattr(self, attr):
            x = [f.resolve() for f in self._link_dir.glob('*') if f.is_symlink()]
            setattr(self, attr, x)
        return getattr(self, attr)

    @property
    def py2_path(self):
        attr = '_' + sys._getframe().f_code.co_name
        if not hasattr(self, attr):
            setattr(self, attr, Path('/opt/python/2').resolve())
        return getattr(self, attr)

    @property
    def py2(self):
        attr = '_' + sys._getframe().f_code.co_name
        if not hasattr(self, attr):
            setattr(self, attr, tuple(int(x) for x in self.py2_path.name.split('.')))
        return getattr(self, attr)

    @property
    def py3_path(self):
        attr = '_' + sys._getframe().f_code.co_name
        if not hasattr(self, attr):
            setattr(self, attr, Path('/opt/python/3').resolve())
        return getattr(self, attr)

    @property
    def py3(self):
        attr = '_' + sys._getframe().f_code.co_name
        if not hasattr(self, attr):
            setattr(self, attr, tuple(int(x) for x in self.py3_path.name.split('.')))
        return getattr(self, attr)

    def latest_versions(self, out=sys.stdout):
        print('py2', self.py2, file=out)
        print('py3', self.py3, file=out)

    def python_version_in_venv(self, d):
        python_cmd = [str(d / 'bin' / 'python'), '--version']
        res = check_output(python_cmd, stderr=subprocess.STDOUT).split()[-1]
        return tuple(int(x) for x in res.split('.'))

    # update all with
    # for x in /opt/util/*/bin/pip ; do $x install -U pip;  done
    def packages_in_venv(self, d, pre=False, outdated=False):
        pre = ['--pre'] if pre else []
        pip_args = ['list']
        if outdated:
            pip_args.extend(['--outdated', '--format=columns'])
        # pip_args_no_legacy = ['list']
        pip_cmd = [str(d / 'bin' / 'pip')]
        res = []
        for line in check_output(pip_cmd + pip_args + pre,
                                 stderr=subprocess.STDOUT).splitlines():
            if line.startswith('-----'):
                continue
            if line.startswith('Package '):
                continue
            res.append(line)
        return res

    def upgrade_version(self, v, py3=False):
        alt = ''
        python_bin = None
        if py3 or v[0] == 3:
            if v < self.py3:
                alt = str(self.py3)
                python_bin = self.py3_path / 'bin' / 'python'
            elif v > self.py3:
                raise NotImplementedError
        elif v[0] == 2:
            if v < self.py2:
                alt = str(self.py2)
                python_bin = self.py2_path / 'bin' / 'python'
            elif v > self.py2:
                raise NotImplementedError
        else:
            raise NotImplementedError
        return alt, python_bin

    def version(self):
        self.latest_versions()
        dir_len = 0
        for d in self.venv_dirs:
            if len(str(d)) > dir_len:
                dir_len = len(str(d))

        for d in self.venv_dirs:
            v = self.python_version_in_venv(d)
            alt, pb = self.upgrade_version(v)
            print('{0:{1}s} {2:10s}  {3:10s}  {4}'.format(str(d), dir_len, str(v), alt, pb))
            if alt:
                for line in (self.packages_in_venv(d)):
                    print(' ', line)
            sys.stdout.flush()

    def install(self):
        os.environ['PATH'] = os.path.dirname(sys.executable) + ':' + os.environ['PATH']
        for d in self._args.dir:
            p = Path(d)
            if self._args.pkg:
                assert len(self._args.dir) == 1
                pkg = self._args.pkg
            else:
                pkg = Path(d).name
            print('pkg', pkg)
            cmd = ['virtualenv']
            if self._args.python:
                py_path = self._args.python.resolve()
            else:
                # if not set explicitly, would get the version from virtualenv
                py_path = self.py3_path / 'bin' / 'python'
            cmd.extend(['--python', py_path])
            full_cmd = cmd + [p]
            check_output(full_cmd, verbose=2)
            check_output([p / 'bin' / 'pip', 'install', pkg], verbose=2)
            self.create_link(p, pkg)
            if self._args.link:
                lib_dir = p / 'lib'
                lib_dir = list(lib_dir.glob('python*'))[0]
                site_packages = lib_dir / 'site-packages'
                print('sp', site_packages)

    def create_link(self, path, pkg=None):
        util = path / 'bin' / (path.stem)
        if pkg is None:
            pkg = path.stem  # lazy...
        alt_util = path / 'bin' / (pkg)
        if not util.exists() and not alt_util.exists():
            print('util', util, 'not found create link by hand')
            return
        if not util.exists():
            util = alt_util
        src = self._link_dir / util.stem
        if src.exists():
            return
        print('creating link for', util, 'from', src)
        print()
        try:
            src.symlink_to(util)
        except:
            cmd = 'sudo ln -s {} {}'.format(util, src)
            print('running', cmd)
            os.system(cmd)


def check_output(*args, **kw):
    import subprocess
    verbose = kw.pop('verbose', 0)
    largs = list(args)
    largs[0] = [str(s) for s in largs[0]]
    if verbose > 1:
        print('cmd', largs[0])
    res = subprocess.check_output(*largs, **kw).decode('utf-8')
    if verbose > 0:
        print(res)
    return res


if __name__ == "__main__":
    print("change directory if you're doing python -m virtualenvutils")
