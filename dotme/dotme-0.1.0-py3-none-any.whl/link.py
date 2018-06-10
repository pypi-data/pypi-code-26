import os
import shutil
import filecmp
from .utils import OPTIONS, Status, Connection, BackupSuffix


class Link:
    def __init__(self, link_home: str, link_conf: dict):
        self.home = link_home
        self.options = link_conf
        self.name = self.options['src']
        self.options['src'] = os.path.join(self.home, self.options['src'])
        self.src = self.options['src']
        self.dst = self.options['dst']
        self.status = (self.get_status(self.src), self.get_status(self.dst))
        self.connection = self.get_connection()

    @staticmethod
    def get_merged_options(link_conf: dict, default_conf: dict):
        opts = OPTIONS.copy()
        for conf in (default_conf, link_conf):  # Order is very important
            for key, value in conf.items():
                if key in OPTIONS:
                    if value:
                        opts[key] = value

        return opts

    @staticmethod
    def get_status(path: str):
        if os.path.islink(path):
            return Status.Symlink
        elif not os.path.exists(path):
            return Status.Empty
        elif os.path.isfile(path):
            return Status.File
        else:
            return Status.Dir

    def get_connection(self):
        if self.status[1] == Status.Symlink and os.readlink(self.dst) == self.src:
                return Connection.Ok
        elif self.status[0] == Status.File and self.status[1] == Status.File:
            if filecmp.cmp(self.src, self.dst):
                return Connection.Ok
        elif self.status[0] in (Status.File, Status.Dir) and self.status[1] in (Status.File, Status.Dir):
            return Connection.Unknown

        return Connection.Broken

    def refresh(self):
        self.status = (self.get_status(self.src), self.get_status(self.dst))
        self.connection = self.get_connection()

    def src_to_dst(self, force: bool):
        status = [False, 'Did nothing']
        if not self.status[0] in (Status.File, Status.Dir):
            status = [False, 'src does not exit']
            return status

        # If dst is a symlink, remove it
        if self.status[1] == Status.Symlink:
            os.remove(self.dst)

        # If dst does not exist, make sure it's parent dir exists
        if self.status[1] == Status.Empty:
            dirname = os.path.dirname(self.dst)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

        # If dst is a file/dir and force = True, backup it
        if self.status[1] in (Status.File, Status.Dir) and force:
                new = self.dst + BackupSuffix().value
                os.rename(self.dst, new)

        if not os.path.exists(self.dst):
            try:
                if self.options['copy']:
                    if self.status[0] == Status.Dir:
                        shutil.copytree(self.src, self.dst)
                    else:
                        shutil.copyfile(self.src, self.dst)
                else:
                    os.symlink(self.src, self.dst)
                status = [True, 'Successfully linked']
                return status
            except Exception as e:
                status[1] = e.args
                return status
        else:
            status[1] = 'dst is not a symlink, use --force to override'

        return status

    def dst_to_src(self, force: bool):
        status = [False, 'Did nothing']
        if not self.status[1] in (Status.File, Status.Dir):
            status[1] = 'dst does not exit'
            return status

        if self.status[0] in (Status.File, Status.Dir) and force:
                new = self.src + BackupSuffix().value
                os.rename(self.src, new)

        if not os.path.exists(self.src):
            try:
                if self.status[1] == Status.Dir:
                    shutil.copytree(self.dst, self.src)
                else:
                    shutil.copyfile(self.dst, self.src)
                if not self.options['copy']:
                    if os.path.isfile(self.dst):
                        os.remove(self.dst)
                    elif os.path.isdir(self.dst):
                        shutil.rmtree(self.dst)

                    self.refresh()
                    self.src_to_dst(force)
                status = [True, 'Successfully collected']
                return status
            except Exception as e:
                status[1] = e.args
                return status
        else:
            status[1] = 'src is not a symlink, use --force to override'

        return status
