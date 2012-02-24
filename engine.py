from ctypes import *

dll = None

def init(dll_path, dawg_path):
    global dll
    dll = CDLL(dll_path)
    dll.init(dawg_path)

def uninit():
    dll.uninit()
