#!/usr/bin/env python

u"""
Python 2/3 Compatibility and Type Checking Helpers
"""

import sys

PY2 = (sys.version_info.major < 3)
PY3 = (sys.version_info.major >= 3)


def check(val, match_types):
    if type(match_types) != list:
        raise Exception(u"Match Types must be list")
    for match_type in match_types:
        if _check_type(val, match_type):
            return True
    bad_types_out = _repr_types(match_types)
    bad_msg = (
        u"Value: %s; Type Found: %s; Valid types are: %s" % (
            val,
            type(val),
            bad_types_out
        )
    )
    raise Exception(bad_msg)


def to_string(val):
    if PY2:
        return unicode(val)
    if PY3:
        return str(val)
    raise Exception(u"Unknown Version")


def _check_type(val, match_type_any):
    if match_type_any is None:
        return _check_type_none(val)
    if type(match_type_any) == type:
        if (
                repr(match_type_any) in [
                    u"<class 'str'>",
                    u"<class 'unicode'>",
                    u"<class 'bytes'>"
                ]
        ):
            raise Exception(u"Bad match type: %s" % match_type_any)
        return _check_type_for(val, match_type_any)
    if _check_type_string(match_type_any):
        if match_type_any == u"jsonable":
            return _check_type_jsonable(val)
        if match_type_any == u"stringable":
            return _check_type_stringable(val)
        if match_type_any == u"string":
            return _check_type_string(val)
        if match_type_any == u"bytes":
            return _check_type_bytes(val)
    raise Exception(u"Invalid match type: %s " % match_type_any)


def _check_type_none(val):
    return (val is None)


def _check_type_for(val, match_type):
    return (type(val) == match_type)


def _repr_type(match_type_any):
    if _check_type_string(match_type_any):
        if match_type_any == u"string":
            return _repr_type_string()
        if match_type_any == u"bytes":
            return _repr_type_bytes()
    return repr(match_type_any)


def _repr_type_string():
    if PY2:
        return u"unicode"
    if PY3:
        return u"str"
    raise Exception(u"Unknown Py version")


def _repr_type_bytes():
    if PY2:
        return u"str"
    if PY3:
        return u"bytes"
    raise Exception(u"Unknown Py version")


def _repr_types(match_types):
    ret = u" ".join([u"[", u" | ".join(map(_repr_type, match_types)), u"]"])
    return ret


def _check_type_jsonable(val):
    return (
        _check_type_string(val) or
        type(val) == int or
        type(val) == float
    )


def _check_type_stringable(val):
    return ((val is not None) and hasattr(val, u"__str__"))


def _check_type_string(val):
    return (
        (PY2 and (type(val) == unicode)) or
        (PY3 and (type(val) == str))
    )


def _check_type_bytes(val):
    return (
        (PY2 and (type(val) == str)) or
        (PY3 and (type(val) == bytes))
    )
