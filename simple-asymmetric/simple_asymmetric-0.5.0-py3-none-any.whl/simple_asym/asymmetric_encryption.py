import base64
from typing import Dict, Union, cast, List, Tuple

from .exceptions import (
    MissingSymmetricKeyException, MissingRsaKeyPairException)
from .crypto import (
    decrypt, encrypt, generate_keys, export_private_key, export_public_key,
    import_key_pair, rsa_decrypt, rsa_encrypt, generate_symmetric_key
)


KeyPair = Dict[str, bytes]
StrOrBytes = Union[str, bytes]


def to_base64(input: bytes) -> str:
    return base64.b64encode(input).decode()


def from_base64(input: str) -> bytes:
    return base64.b64decode(input)


def force_to_base64(input: StrOrBytes) -> str:
    if type(input) is bytes:
        result = to_base64(cast(bytes, input))
    else:
        result = cast(str, input)
    return result


class Asym():
    key_pair: KeyPair = None
    symmetric_key: bytes = None

    def make_rsa_keys(self, password: str = None) -> Tuple[str, str]:
        """ Makes new private key and sets for internal usage
        Return [private_key, public_key] as str. If password is set,
        the private key will be encrypted and ciphertext will be returned
        """
        self.key_pair = generate_keys()
        public_key = export_public_key(self.key_pair)
        private_key = export_private_key(self.key_pair, password)
        return (private_key, public_key)

    def set_key_pair(
        self, public_key: str, private_key: str, password: str = None
    ) -> KeyPair:
        """ Import a public and private key pair for Asym object usage (RSA
        encryption and decryption)
        """
        self.key_pair = import_key_pair(public_key, private_key, password)
        return self.key_pair

    def get_public_key(self) -> str:
        """ Get base64 version of public key """
        return to_base64(self.key_pair['public_key'])

    def get_symmetric_key(self) -> str:
        """ Return symmetric key in plain (unecrypted) base64 format """
        return to_base64(self.symmetric_key)

    def rsa_encrypt(
        self, public_key: str, plaintext: StrOrBytes, use_base64=True
    ) -> StrOrBytes:
        """ Perform RSA encryption (asymmetric)
        :param public_key: "Their" public key we want to encrypt something for
        :param plaintext: plaintext string to encrypt
        :param use_base64: Default True, return in base64 format (else bytes)
        """
        plaintext = force_to_base64(plaintext)
        return rsa_encrypt(public_key, plaintext, use_base64)

    def rsa_decrypt(self, ciphertext: str):
        """ Perform RSA Decryption (asymmetric)
        :param ciphertext: ciphertext string to decrypt
        """
        if not self.key_pair['private_key']:
            raise MissingRsaKeyPairException()
        return rsa_decrypt(
            self.key_pair['public_key'],
            self.key_pair['private_key'],
            ciphertext)

    def make_symmetric_key(self) -> str:
        """ Generate random symmetric key for internal usage and return base64
        string of it
        """
        self.symmetric_key = cast(bytes, generate_symmetric_key())
        return to_base64(self.symmetric_key)

    def set_symmetric_key(self, key: StrOrBytes):
        """ Set asym symmetric key (used for secret key encryption)
        :param key: base64 or binary key
        """
        if type(key) is str:
            self.symmetric_key = from_base64(cast(str, key))
        else:
            self.symmetric_key = cast(bytes, key)

    def get_encrypted_symmetric_key(self, public_key: str) -> str:
        """ Get encrypted version of symmetric key to share
        :param public_key: "Their" public key
        """
        key = self.rsa_encrypt(public_key, self.symmetric_key)
        return cast(str, key)

    def set_symmetric_key_from_encrypted(self, ciphertext: str):
        """ Set the symmetric (shared) key from encrypted ciphertext.
        :param ciphertext: base64 string of ciphertext version of key
        """
        decrypted_key = self.rsa_decrypt(ciphertext)
        return self.set_symmetric_key(decrypted_key)

    def encrypt(self, plaintext: str) -> str:
        if not self.symmetric_key:
            raise MissingSymmetricKeyException()
        return encrypt(self.symmetric_key, plaintext)

    def decrypt(self, ciphertext: str) -> str:
        if not self.symmetric_key:
            raise MissingSymmetricKeyException()
        return decrypt(self.symmetric_key, ciphertext)
