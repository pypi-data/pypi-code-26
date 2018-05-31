from hashlib import md5, sha1, sha256, sha512
from pros import Command, catalog


class Basehasher(Command):
    implement = frozenset({'binary', 'text'})
    sources = frozenset({'text'})

    def process(self, **kwargs):
        while 1:
            source, message = yield
            hasher = self.hasher(message)
            if kwargs['hex']:
                yield hasher.hexdigest()
            else:
                yield hasher.digest()

    @staticmethod
    def get_parser(parser):
        parser.add_argument('--hex', action='store_true', default=False, help='return hex digest instead of binary')
        return parser


@catalog.register
class MD5Hasher(Basehasher):
    """Hash text by MD5 algorithm
    """
    name = 'hash/md5'
    hasher = md5


@catalog.register
class SHA1Hasher(Basehasher):
    """Hash text by SHA1 algorithm
    """
    name = 'hash/sha1'
    hasher = sha1


@catalog.register
class SHA256Hasher(Basehasher):
    """Hash text by SHA256 algorithm
    """
    name = 'hash/sha256'
    hasher = sha256


@catalog.register
class SHA512Hasher(Basehasher):
    """Hash text by SHA512 algorithm
    """
    name = 'hash/sha512'
    hasher = sha512
