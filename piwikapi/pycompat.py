#!/usr/bin/env python

"""
Python 2/3 Compatibility Helpers
"""

import sys

PY2 = (sys.version_info.major < 3)
PY3 = (sys.version_info.major >= 3)


def use_string_type(val):
    if PY2:
        return 'unicode | str'
    if PY3:
        return 'str'
    raise Exception("Unknown Version")


def to_string(val):
    if PY2:
        return unicode(val)
    if PY3:
        return str(val)
    raise Exception("Unknown Version")


def is_string(val):
    return (
        (PY2 and (type(val) in [unicode, str])) or
        (PY3 and (type(val) == str))
    )
