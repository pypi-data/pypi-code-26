import os.path
from argparse import ArgumentTypeError

from ..config import Config


def check_filetype(filepath):
    _, ext = filepath.rsplit('.', 1)

    if ext == 'json':
        return 'json'
    elif ext in ['yaml', 'yml']:
        try:
            import yaml  # noqa
            return 'yaml'
        except ImportError as exc:
            msg = 'Install the [yaml] extras to use YAML-based config files.'
            raise ArgumentTypeError(msg) from exc
    else:
        raise ArgumentTypeError(f"Unrecognized vendor file type: '{ext}'.")


class Command:

    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.
        """
        parser.add_argument('--vendor-file', metavar='FILENAME', dest='config',
                            help="The file path of the vendor file. Defaults to the "
                                 "'VENDORFILE' environment variable, and will fallback "
                                 "to any of 'vendor.json', 'vendor.yaml', 'vendor.yml'.")

    def get_config(self, options):
        # Default to VENDORFILE if no value provided
        filename = options.config or os.environ.get('VENDORFILE')

        # If provided a ``filename``, it must exist.
        if filename:
            filepath = os.path.abspath(filename)
            if not os.path.exists(filepath):
                raise self.error(f"Could not find vendor file, tried: '{filepath}'.")

        # If no ``filename`` is provided, fallback to commone filenames.
        else:
            defaults = ['vendor.json', 'vendor.yaml', 'vendor.yml']
            defaults = [os.path.abspath(name) for name in defaults]

            for filepath in defaults:
                if os.path.exists(filepath):
                    break
            else:
                attempts = ', '.join(f"'{path}'" for path in defaults)
                raise self.error(f"Could not find vendor file, tried: {attempts}.")

        # Return the config object
        filetype = check_filetype(filepath)
        return Config(filepath, filetype)

    def handle(self, options):
        """
        The actual logic of the command. Subclasses must implement this method.
        """
        raise NotImplementedError('Subclasses of Command must provide a handle() method.')
