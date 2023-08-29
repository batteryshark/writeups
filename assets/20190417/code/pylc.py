# Limited Ctypes Module for the Senselock LC (CLAVE2) API
import os
from ctypes import *
import binascii

DEFAULT_LC_PASSWORD = "12345678".encode('ascii')
DEFAULT_DEV_ID = 0x3F3F3F3F
INDEX = 0
USER_TYPE = 1
lc_dll = WinDLL(os.path.join(os.path.dirname(__file__),"LC.dll"))

lc_dll.LC_open.argtypes = [c_uint32, c_uint32, POINTER(c_int32)]
lc_dll.LC_open.restype = c_uint32
lc_dll.LC_passwd.restype = c_uint32
lc_dll.LC_passwd.argtypes = [c_int32, c_uint32, POINTER(c_char)]


def detect_arch():
    return sizeof(c_voidp) * 8


def lcc_init(dev_id=DEFAULT_DEV_ID, password=DEFAULT_LC_PASSWORD):
    handle = c_int32(0)
    res = lc_dll.LC_open(dev_id, INDEX, byref(handle))
    if res != 0:
        print("Open Failed! :%04X" % res)
        return False, None
    res = lc_dll.LC_passwd(handle.value, USER_TYPE, password)
    if res != 0:
        print("passwd Failed! :%04X" % res)
        return False, None
    return True, handle


def lc_encrypt(dev_id, dongle_passwd, in_data):
    if detect_arch == 64:
        print("Native Bindings for 64 bit are not currently supported")
        while ndec is b"":
            t_ndec = input("Enter the ascii hex of the output bytes: ")
            try:
                ndec = binascii.unhexlify(t_ndec)
            except:
                print("Error - Not a Hex String")
                continue
        return True, ndec

    status, handle = lcc_init(dev_id, dongle_passwd)
    if (status is False):
        return False, b""
    outdata = (c_ubyte * len(in_data))()
    res = lc_dll.LC_encrypt(handle, in_data, outdata)
    if res != 0:
        print("encrypt Failed! :%04X" % res)
        return False, b""
    return True, bytes(outdata[:])


def lc_decrypt(dev_id, dongle_passwd, in_data):
    if (detect_arch == 64):
        print("Native Bindings for 64 bit are not currently supported")
        while ndec is b"":
            t_ndec = input("Enter the ascii hex of the output bytes: ")
            try:
                ndec = binascii.unhexlify(t_ndec)
            except:
                print("Error - Not a Hex String")
                continue
        return True, ndec

    status, handle = lcc_init(dev_id, dongle_passwd)
    if (status is False):
        return False, b""
    outdata = (c_ubyte * len(in_data))()
    res = lc_dll.LC_decrypt(handle, in_data, outdata)
    if res != 0:
        print("decrypt Failed! :%04X" % res)
        return False, b""
    return True, bytes(outdata[:])
