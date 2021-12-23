# -*- coding: utf-8 -*-
"""
    serialize.msgpack
    ~~~~~~~~~~~~~~~~~

    Helpers for Msgpack Serialization.

    See https://pypi.python.org/pypi/msgpack-python for more details.

    :copyright: (c) 2016 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""

from . import all

try:
    import msgpack
except ImportError:
    all.register_unavailable("msgpack", pkg="msgpack-python")
    raise


def dumps(obj):
    return msgpack.packb(obj, default=all.encode)


def loads(content):
    return msgpack.unpackb(content, object_hook=all.decode, raw=False)


all.register_format("msgpack", dumps, loads)
