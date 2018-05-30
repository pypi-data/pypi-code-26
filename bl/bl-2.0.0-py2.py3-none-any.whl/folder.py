
import logging, pathlib, shutil
log = logging.getLogger(__name__)

def rmtree_warn(function, path, excinfo):
    log.warn("Could not remove %s: %s" % (path, excinfo()[1]))    

class Folder(pathlib.Path):

    def __init__(self, *segments):
        super().__init__(*segments)
        assert self.is_dir()

    def rmtree(self, ignore_errors=False, onerror=rmtree_warn):
        shutil.rmtree(str(self), ignore_errors=False, onerror=rmtree_warn)
