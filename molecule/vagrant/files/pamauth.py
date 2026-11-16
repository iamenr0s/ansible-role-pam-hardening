#!/usr/bin/python3
"""Run pam_authenticate for USER with PASSWORD against SERVICE; exit with the PAM return code (0 = success)."""
import ctypes
import ctypes.util
import sys

user, password, service = sys.argv[1:4]
libpam = ctypes.CDLL(ctypes.util.find_library("pam"))
libc = ctypes.CDLL(ctypes.util.find_library("c"))
libc.calloc.restype = ctypes.c_void_p
libc.calloc.argtypes = [ctypes.c_size_t, ctypes.c_size_t]
libc.strdup.restype = ctypes.c_void_p
libc.strdup.argtypes = [ctypes.c_char_p]


class Message(ctypes.Structure):
    _fields_ = [("msg_style", ctypes.c_int), ("msg", ctypes.c_char_p)]


class Response(ctypes.Structure):
    _fields_ = [("resp", ctypes.c_void_p), ("resp_retcode", ctypes.c_int)]


CONV = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(Message)),
                        ctypes.POINTER(ctypes.POINTER(Response)), ctypes.c_void_p)


class Conv(ctypes.Structure):
    _fields_ = [("conv", CONV), ("appdata_ptr", ctypes.c_void_p)]


def converse(n, msg, resp, _app):
    addr = libc.calloc(n, ctypes.sizeof(Response))
    resp[0] = ctypes.cast(addr, ctypes.POINTER(Response))
    for i in range(n):
        resp[0][i].resp = libc.strdup(password.encode())
    return 0


conv = Conv(CONV(converse), None)
handle = ctypes.c_void_p()
libpam.pam_start.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(Conv), ctypes.POINTER(ctypes.c_void_p)]
rc = libpam.pam_start(service.encode(), user.encode(), ctypes.byref(conv), ctypes.byref(handle))
if rc == 0:
    rc = libpam.pam_authenticate(handle, 0)
    libpam.pam_end(handle, rc)
print(rc)
sys.exit(rc)
