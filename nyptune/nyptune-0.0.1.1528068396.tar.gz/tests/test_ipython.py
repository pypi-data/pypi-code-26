import nyptune
from nyptune.handler.path import PathHandler
from pathlib import *
import tempfile
import IPython
from ipykernel.inprocess.manager import InProcessKernelManager


def setup_module(module):
    global km
    km = InProcessKernelManager()
    km.start_kernel()
    kc = km.client()
    kc.start_channels()
    kc.wait_for_ready()


def generate_file(name, content):
    path = Path(tempfile.gettempdir()) / name
    with open(path, "w") as file:
        file.write(content)
    return path


def test_ipython_shell_exists():
    km.kernel.shell.run_cell("a = 1")
    assert km.kernel.shell.user_ns["a"] == 1


def test_happy_path():
    km.kernel.shell.run_cell("""from pathlib import Path;""")
    path = generate_file("foo", "hello world")
    magics = nyptune.magic.CacheMagics(shell=km.kernel.shell)
    magics.nyptune_name("testing")
    km.kernel.shell.run_cell(f"file = Path('{path}')")
    magics.cache("file")
    assert magics.is_cached("file")


def test_path_handler():
    path = generate_file("foo", "hello world")
    handler = PathHandler()
    assert isinstance(path, Path)
    assert handler.understands(path)
