import os.path
import shutil
import tarfile
import tempfile

from .base import Command
from ..npm import Client


class Install(Command):
    """Download and install the vendored packages and their dependencies."""

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-y', '--yes', action='store_true', default=False,
                            dest='ignore', help="Ignore all prompts.")

    def handle(self, options):
        config = self.get_config(options)
        client = Client(config.metadata_dir, config.registry)

        if not options.ignore:
            print(f'Proceeding may erase files in {config.location_dir}.')
            confirm = input('Are you sure you want to do this? [y/N] ')
            if confirm.lower() in ['', 'n', 'no']:
                return

        # Get pacakge metadata
        for package in config.packages:
            client.get_metadata(package['package'])

        # Download archives and checksum against lockfile
        for package in config.packages:
            archive = client.get_archive(package['package'], package['version'])
            client.checksum(archive, package['shasum'])

        # Clear existing directories in install location and untar the archives
        os.makedirs(config.location_dir, exist_ok=True)
        for package in config.packages:
            archive = client.get_archive(package['package'], package['version'])
            install = os.path.join(config.location_dir, package['package'])

            with tempfile.TemporaryDirectory() as unpack:
                with tarfile.open(archive, 'r:gz') as tar:
                    tar.extractall(unpack)

                if os.path.exists(install):
                    shutil.rmtree(install)
                shutil.move(os.path.join(unpack, 'package'), install)
