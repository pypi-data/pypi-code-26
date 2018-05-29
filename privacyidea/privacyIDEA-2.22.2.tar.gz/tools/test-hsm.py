#!/usr/bin/env python
# -*- coding: utf-8 -*-
from privacyidea.lib.security.aeshsm import AESHardwareSecurityModule

your_password = "please-change-this"
slot = 0

module = "/usr/safenet/lunaclient/lib/libCryptoki2_64.so"


p = AESHardwareSecurityModule({"module": module,
                               "slot": slot,
                               "key_label": "privacyidea",
                               "password": your_password})

print("=== Test encryption of passwords ===")
data = "topSekr3t" * 16
crypted = p.encrypt_password(data)
text = p.decrypt_password(crypted)
assert (text == data)
print("password encrypt/decrypt test successful")

# pin
print("=== Test encryption of PIN ===")
pin = "topSekr3t"
crypted = p.encrypt_pin(pin)
text = p.decrypt_pin(crypted)
assert (text == pin)
print("pin encrypt/decrypt test successful")

# random
print("=== Test getting random data from HSM ===")
iv = p.random(16)
plain = p.random(128)
print("random test successful")

# generic encrypt / decrypt
print("=== Test encryption generic data like Token Seed ===")
cipher = p.encrypt(plain, iv)
assert (plain != cipher)
text = p.decrypt(cipher, iv)
assert (text == plain)
print("generic encrypt/decrypt test successful")


print("=== Text pushing password to module ===")
p = AESHardwareSecurityModule({"module": module,
                               "slot": slot,
                               "key_label": "privacyidea"})
p.setup_module({"password": your_password})
print("Initializing HSM succssfull.")

# generic encrypt / decrypt
print("=== Test encryption generic data like Token Seed ===")
cipher = p.encrypt(plain, iv)
assert (plain != cipher)
text = p.decrypt(cipher, iv)
assert (text == plain)
print("generic encrypt/decrypt test successful")

