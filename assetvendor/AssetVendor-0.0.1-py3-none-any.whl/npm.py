import hashlib
import json
import os.path
from urllib import parse
from urllib.request import Request, urlopen

try:
    from packaging.specifiers import SpecifierSet
except ImportError:
    from pip._vendor.packaging.specifiers import SpecifierSet


def download(request, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with urlopen(request) as response:
        encoding = response.headers.get_content_charset()
        contents = response.read()

        if encoding is not None:
            with open(path, 'w') as file:
                file.write(contents.decode(encoding))

        else:
            with open(path, 'wb') as file:
                file.write(contents)


class Metadata:
    """Package metadata wrapper utility.

    This class encapsulates all of the necessary operations for inspecting a
    package's metadata.
    """

    def __init__(self, data):
        self._data = data

    def get_tags(self):
        """Get the dictionary of distribution tags and their versions."""
        return self._data['dist-tags'].copy()

    def get_tarball(self, version):
        return self._data['versions'][version]['dist']['tarball']

    def get_shasum(self, version):
        return self._data['versions'][version]['dist']['shasum']

    def get_compatible_versions(self, version_range):
        """Gets the set of versions that satisfy the given version range.

        Args:
            version_range (str): Specifies the range of acceptable versions.
                This **must** be a valid PEP 440 range, not an NPM range.
                https://packaging.pypa.io/en/latest/specifiers/
                https://www.python.org/dev/peps/pep-0440/
        """
        if isinstance(version_range, str):
            version_range = SpecifierSet(version_range)

        return version_range.filter(list(self._data['versions']))


class Client:
    """Client that manages interactions with an NPM registry.

    Attributes:
        metadata_dir: Directory where AssetVendor's metadata is stored.
        archives_dir: Subdirectory of the ``.metadata_dir`` where distribution
            archives are stored.
        registry: The URL of the NPM registry. This defaults to the public
            NPM registry, but may be overridden for private registries.
    """
    registry = 'https://registry.npmjs.com'

    def __init__(self, metadata_dir, registry=None):
        self.metadata_dir = metadata_dir
        self.archives_dir = os.path.join(metadata_dir, 'archives')
        if registry is not None:
            self.registry = registry

    def get_metadata(self, package, update=False):
        """Get the metadata for a package.

        The metadata will be downloaded if necessary or if forced.

        Args:
            package (str): The package's name.
            update (bool): Force an update of the package metadata.
                Defaults to ``False``.

        Returns:
            Metadata: A metadata wrapper for the response json.
        """
        path = os.path.join(self.metadata_dir, f'{package}.json')
        if not os.path.exists(path) or update:
            url = parse.urljoin(self.registry, package)
            download(Request(url), path)

        with open(path, 'r') as file:
            return Metadata(json.load(file))

    def get_archive(self, package, version, update=False):
        """Get the distribution archive for a specific package version.

        The archive will be downloaded if necessary or if forced.

        Args:
            package (str): The package's name.
            version (str): The package version.
            update (bool): Force an update of the distribution archive.
                Defaults to to ``False``.

        Returns:
            str: The absolute path of the archive file.

        Raises:
            RuntimeError: The archive checksum failed.
        """
        metadata = self.get_metadata(package, update)

        url = metadata.get_tarball(version)
        path = os.path.join(self.archives_dir, os.path.split(url)[1])
        if not os.path.exists(path) or update:
            download(Request(url), path)

        if not self.checksum(path, metadata.get_shasum(version)):
            raise RuntimeError(f"The archive shasum ({path}) failed to "
                               f"match the version checksum ({version}).")

        return path

    def checksum(self, archive, shasum):
        """Check the archive's computed shasum against the provided value.

        Args:
            archive (str): The absolute path of the archive file.
            shasum (str): The shasum to check against.

        Returns:
            bool: Whether the shasums match.
        """
        with open(archive, 'rb') as file:
            computed = hashlib.sha1(file.read()).hexdigest()
            return computed == shasum
