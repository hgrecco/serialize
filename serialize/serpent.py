# -*- coding: utf-8 -*-
"""
    serialize.phpserialize
    ~~~~~~~~~~~~~~~~~~~~~~

    Helpers for Serpent Serialization.

    See https://pypi.python.org/pypi/serpent for more details.

    :copyright: (c) 2016 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""

from . import all

try:
    import serpent
except ImportError:
    all.register_unavailable("serpent", pkg="serpent")
    raise


class MySerializer(serpent.Serializer):
    def _serialize(self, obj, out, level):
        obj = all.encode(obj)
        return super()._serialize(obj, out, level)


def dumps(obj):
    return MySerializer().serialize(obj)


def loads(content):
    return all.traverse_and_decode(serpent.loads(content))


all.register_format("serpent", dumps, loads)
