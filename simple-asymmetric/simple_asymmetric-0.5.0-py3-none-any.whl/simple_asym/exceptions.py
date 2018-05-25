class AsymException(Exception):
    pass


class MissingKeyException(AsymException):
    pass


class MissingSymmetricKeyException(MissingKeyException):
    message = "Missing Symmetric key. Set or generate one"


class MissingRsaKeyPairException(MissingKeyException):
    message = "Missing RSA key pair. Set or generate one to use RSA encryption"
