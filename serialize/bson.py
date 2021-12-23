# -*- coding: utf-8 -*-
"""
    serialize.dill
    ~~~~~~~~~~~~~~

    Helpers for Bson Serialization.

    See https://pypi.python.org/pypi/bson for more details.

    :copyright: (c) 2016 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""

from . import all

try:
    import bson
except ImportError:
    all.register_unavailable("bson", pkg="bson")
    raise


# In the BSON format the top level object must be a dictionary.
# If necessary, we put the object in dummy dictionary
# under the key __bson_follow__


def dumps(obj):
    if not isinstance(obj, dict):
        obj = dict(__bson_follow__=obj)
    return bson.dumps(all.traverse_and_encode(obj))


def loads(content):
    obj = all.traverse_and_decode(bson.loads(content))
    return obj.get("__bson_follow__", obj)


all.register_format("bson", dumps, loads)
