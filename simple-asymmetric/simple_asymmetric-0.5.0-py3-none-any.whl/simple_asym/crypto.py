import base64
import pysodium
from typing import Union


def generate_keys():
    keys = pysodium.crypto_box_keypair()
    return {'public_key': keys[0], 'private_key': keys[1]}


def hash_password(password, salt):
    if type(salt) is str:
        salt = base64.b64decode(salt)

    OPSLIMIT = 4
    MEMLIMIT = 33554432
    ALG = 1
    hashed_password = pysodium.crypto_pwhash(
        pysodium.crypto_box_SEEDBYTES,
        password,
        salt,
        OPSLIMIT,
        MEMLIMIT,
        ALG,
    )
    return hashed_password


def make_salt():
    salt = pysodium.randombytes(pysodium.crypto_pwhash_SALTBYTES)
    return salt


def encrypt(key: Union[str, bytes], message, use_base64=True):
    if type(key) is str:
        key = base64.b64decode(key)
    if type(message) is str:
        message = message.encode()
    nonce = pysodium.randombytes(pysodium.crypto_secretbox_NONCEBYTES)
    combined_buffer = nonce + pysodium.crypto_secretbox(message, nonce, key)
    if use_base64:
        return base64.b64encode(combined_buffer).decode()
    return combined_buffer


def decrypt(
    key: Union[str, bytes], ciphertext: Union[str, bytes], make_text=True
):
    if type(key) is str:
        key = base64.b64decode(key)
    if type(ciphertext) is str:
        ciphertext = base64.b64decode(ciphertext)
    nonce = ciphertext[:pysodium.crypto_secretbox_NONCEBYTES]
    encrypted_message = ciphertext[pysodium.crypto_secretbox_NONCEBYTES:]
    decrypted_message = pysodium.crypto_secretbox_open(
        encrypted_message,
        nonce,
        key,
    )
    if make_text:
        return decrypted_message.decode()
    return decrypted_message


def export_private_key(key_pair, password=None) -> str:
    if password:
        salt = make_salt()
        hashed_password = hash_password(password, salt)
        ciphertext = encrypt(hashed_password, key_pair['private_key'], False)
        combined_buffer = salt + ciphertext
        return base64.b64encode(combined_buffer).decode()
    else:
        return base64.b64encode(key_pair['private_key']).decode()


def export_public_key(key_pair):
    return base64.b64encode(key_pair['public_key']).decode()


def import_key_pair(public_key: str, private_key: str, password=None):
    if password:
        pk = base64.b64decode(private_key)
        salt = pk[:pysodium.crypto_pwhash_SALTBYTES]
        ciphertext = pk[pysodium.crypto_pwhash_SALTBYTES:]
        hash = hash_password(password, salt)
        pk = decrypt(hash, ciphertext, False)
    else:
        pk = base64.b64decode(private_key)
    return {
        'public_key': base64.b64decode(public_key),
        'private_key': pk,
    }


def rsa_encrypt(
    their_public_key: Union[str, bytes],
    plaintext: str,
    use_base64=True,
) -> Union[str, bytes]:
    if type(their_public_key) is str:
        their_public_key = base64.b64decode(their_public_key)

    encrypted_buffer = pysodium.crypto_box_seal(
        plaintext.encode(), their_public_key)
    if use_base64:
        return base64.b64encode(encrypted_buffer).decode()
    return encrypted_buffer


def rsa_decrypt(
    my_public_key: Union[str, bytes],
    my_private_key: Union[str, bytes],
    encrypted_buffer: Union[str, bytes],
) -> Union[str, bytes]:
    if type(my_public_key) is str:
        my_public_key = base64.b64decode(my_public_key)
    if type(my_private_key) is str:
        my_private_key = base64.b64decode(my_private_key)
    if type(encrypted_buffer) is str:
        encrypted_buffer = base64.b64decode(encrypted_buffer)
    message = pysodium.crypto_box_seal_open(
        encrypted_buffer, my_public_key, my_private_key)

    return message.decode()


def generate_symmetric_key(use_base64=False) -> Union[bytes, str]:
    key = pysodium.randombytes(pysodium.crypto_secretbox_KEYBYTES)
    if use_base64:
        return base64.b64encode(key)
    return key
