from importlib import import_module
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from os.path import abspath


class Loader:
    @staticmethod
    def load_module(name):
        try:
            import_module(name)
        except ImportError:
            return False
        return True

    @staticmethod
    def load_file(path):
        path = Path(path)
        if not path.exists():
            return False
        module_name = path.stem
        full_path = str(path.absolute())
        # load module
        spec = spec_from_file_location(module_name, full_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return True

    @classmethod
    def load_all(cls):
        path = Path(abspath(__file__)).parent.parent / 'commands'
        for fpath in path.iterdir():
            if fpath.suffix == '.py':
                cls.load_file(str(fpath))
