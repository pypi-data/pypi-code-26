import pathlib, os, urllib, shutil
from pathlib import Path
from tqdm import tqdm
import urllib.request


def unlink_f(path):
    if Path(path).is_file():
        os.unlink(path)


def link_f(src, target):
    target = Path(target)
    if target.is_file() or target.is_symlink():
        os.unlink(target)
    try:
        os.link(Path(src).resolve(), target)
    except:
        shutil.copy(Path(src).resolve(), target)


class TqdmUpTo(tqdm):
    """Provides `update_to(n)` which uses `tqdm.update(delta_n)`."""

    def update_to(self, b=1, bsize=1, tsize=None):
        """
        b  : int, optional
            Number of blocks transferred so far [default: 1].
        bsize  : int, optional
            Size of each block (in tqdm units) [default: 1].
        tsize  : int, optional
            Total size (in tqdm units). If [default: None] remains unchanged.
        """
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)  # will also set self.n = b * bsize


def download(url, path):
    with TqdmUpTo(unit="B", unit_scale=True, miniters=1, desc=url.split("/")[-1]) as t:
        urllib.request.urlretrieve(url, path, reporthook=t.update_to, data=None)
    return Path(path)
