from ecc import *
import evt_exception
import libevt


def generate_new_pair():
    libevt.check_lib_init()
    public_key_c = libevt.libevt.ffi.new('evt_public_key_t**')
    private_key_c = libevt.libevt.ffi.new('evt_private_key_t**')
    ret = libevt.libevt.lib.evt_generate_new_pair(public_key_c, private_key_c)
    evt_exception.evt_exception_raiser(ret)
    return PublicKey(public_key_c[0]), PrivateKey(private_key_c[0])
