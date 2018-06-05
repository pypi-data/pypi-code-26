# coding=utf-8
import rsa
from Crypto.Cipher import AES
from Crypto import Random
import binascii

buffer_size = 1024 * 1024 * 16


def gen_rsa_key_pair(public_key_file, private_key_file):
    (pub_key, pri_key) = rsa.newkeys(2048)
    with open(public_key_file, 'w+') as f:
        f.write(pub_key.save_pkcs1().decode())

    with open(private_key_file, 'w+') as f:
        f.write(pri_key.save_pkcs1().decode())


def load_rsa_pub_key(public_key_file):
    with open(public_key_file, 'r') as f:
       return rsa.PublicKey.load_pkcs1(f.read().encode())


def load_rsa_pri_key(private_key_file):
    with open(private_key_file, 'r') as f:
        return rsa.PrivateKey.load_pkcs1(f.read().encode())


def rsa_encrypt_string(msg, pub_key):
    return rsa.encrypt(msg.encode(), pub_key)


def rsa_decrypt_string(msg, pri_key):
    return rsa.decrypt(msg, pri_key).decode()


class AesUtil:

    def __init__(self, aes_key_path=None):
        if aes_key_path is not None:
            self.load_aes_key_iv(aes_key_path)
        else:
            self.key = None
            self.iv = None

    def gen_aes_key_iv(self, aes_key_path):
        self.key = Random.new().read(AES.block_size)
        self.iv = Random.new().read(AES.block_size)
        ase_file = open(aes_key_path, "wb+")
        ase_file.write(self.key)
        ase_file.write(self.iv)
        ase_file.close()

    def load_aes_key_iv(self, aes_key_path):
        ase_file = open(aes_key_path, "rb")
        self.key = ase_file.read(AES.block_size)
        self.iv = ase_file.read(AES.block_size)
        ase_file.close()

    def aes_encrypt_string(self, msg):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        mode = len(msg) % AES.block_size
        msg = msg + " " * (AES.block_size - mode)
        return cipher.encrypt(msg)

    def aes_decrypt_string(self, msg):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return cipher.decrypt(msg).strip()

    def aes_encrypt_file(self, input_path, out_path):
        encrypt_file = open(out_path, "wb+")
        with open(input_path, "rb") as f:
            file_buffer = f.read(buffer_size)
            while file_buffer != "":
                buffer_enc = self.aes_encrypt_string(file_buffer)
                encrypt_file.write(buffer_enc)
                file_buffer = f.read(buffer_size)

        encrypt_file.close()

    def aes_decrypt_file(self, input_path, out_path):
        decrypt_file = open(out_path, "wb+")
        with open(input_path, "rb") as f:
            file_buffer = f.read(buffer_size)
            while file_buffer != "":
                buffer_dec = self.aes_decrypt_string(file_buffer)
                decrypt_file.write(buffer_dec)
                file_buffer = f.read(buffer_size)

        decrypt_file.close()


if __name__ == '__main__':
    # gen_rsa_key_pair("zc.pub", "zc.pri")
    aes_file_path = "zc.aes"
    aes_util = AesUtil(aes_file_path)
    aes_util.aes_encrypt_file("zc.rar", "zc.rar.enc")
    aes_util.aes_decrypt_file("zc.rar.enc", "zc.rar.enc.rar")

