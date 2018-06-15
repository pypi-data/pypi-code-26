import os.path
import sys
import hashlib
from .consts import CACHE_DIR


def get_identity(
    argv=None,
    prefix=CACHE_DIR if CACHE_DIR.endswith("/") else CACHE_DIR + "/",
    suffix=".csv",
    encoding="utf-8",
    hasher=hashlib.sha1,
    extra=None,
):
    """
    get_identity('main')
    '~/.cache/py-resumable/f58ccb5f55e806673664c8e5c56515d07790df41.csv'
    """
    if argv is None:
        argv = sys.argv[:]
        if len(argv) > 0:
            argv[0] = os.path.abspath(argv[0])
        if extra is not None:
            argv.append(extra)
    sha1 = hasher("@".join(argv).encode(encoding))
    identity = "{}{}{}".format(prefix, sha1.hexdigest(), suffix)
    return identity


def with_decoration(filepath, *, prefix):
    """
    >>> with_decoration('./foo/bar.txt', prefix='super-')
    './foo/super-bar.txt'
    """
    d = os.path.dirname(filepath)
    b, ext = os.path.splitext(os.path.basename(filepath))
    return os.path.join(d, "{}{}{}".format(prefix, b, ext))
