#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes
from contextlib import contextmanager


_CFuncPtrOriginal = ctypes._CFuncPtr


class AttrCheck(object):
    def __init__(self, name):
        self.name = name
        self.ignored = False
        self.set = False


class CFuncPtrChecking(ctypes._CFuncPtr):
    """
    Subclass CFuncPtr and add checks for setting attributes before calling.
    """
    # required placeholder
    _flags_ = 0

    # ignore or set flags for attributes
    argtypes_check = AttrCheck('argtypes')
    restype_check = AttrCheck('restype')
    errcheck_check = AttrCheck('errcheck')
    _all_checks = (argtypes_check, restype_check, errcheck_check)

    # prevent the FFI call from actually happening
    prevent_ffi_call = False

    def __call__(self, *args, **kwargs):
        missing = [check.name for check in self._all_checks
                   if not check.ignored and not check.set]
        if missing:
            raise AttributeError('attribute(s) "{}" not set before calling function "{}"'.format(', '.join(missing),
                                                                                                 self.__name__))
        if not self.prevent_ffi_call:
            super(CFuncPtrChecking, self).__call__(*args, **kwargs)

    def __setattr__(self, key, value):
        for check in self._all_checks:
            if key == check.name:
                check.set = True
        super(CFuncPtrChecking, self).__setattr__(key, value)


@contextmanager
def check_ctypes(ignore_argtypes=False, ignore_restype=False, ignore_errcheck=False, prevent_ffi_call=False):
    ctypes._CFuncPtr = CFuncPtrChecking
    ctypes._CFuncPtr.argtypes_check.ignored = ignore_argtypes
    ctypes._CFuncPtr.restype_check.ignored = ignore_restype
    ctypes._CFuncPtr.errcheck_check.ignored = ignore_errcheck
    ctypes._CFuncPtr.prevent_ffi_call = prevent_ffi_call
    try:
        yield
    finally:
        ctypes._CFuncPtr = _CFuncPtrOriginal