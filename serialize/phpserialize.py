# -*- coding: utf-8 -*-
"""
    serialize.phpserialize
    ~~~~~~~~~~~~~~~~~~~~~~

    Helpers for PHP Serialization.

    See https://pypi.python.org/pypi/phpserialize for more details.

    :copyright: (c) 2016 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""

from collections import ChainMap

from . import all

try:
    import phpserialize
except ImportError:
    all.register_unavailable("phpserialize", pkg="phpserialize")
    raise

# PHP Serialize does not support list and tuples, so we convert them to maps.


def _traverse_list_ec(obj, ef, td):
    return dict(
        __class_name__="builtin_list",
        __dumped_obj__={
            ndx: all.traverse_and_encode(val, ef, td) for ndx, val in enumerate(obj)
        },
    )


def _traverse_tuple_ec(obj, ef, td):
    return dict(
        __class_name__="builtin_tuple",
        __dumped_obj__={
            ndx: all.traverse_and_encode(val, ef, td) for ndx, val in enumerate(obj)
        },
    )


CUSTOM_TRAVERSE = ChainMap(
    {list: _traverse_list_ec, tuple: _traverse_tuple_ec}, all.DEFAULT_TRAVERSE_EC
)


def _helper(dct):
    return (mytransverse(dct[n]) for n in range(len(dct)))


CUSTOM_CLASSES_BY_NAME = ChainMap(
    {
        "builtin_list": all.ClassHelper(None, lambda obj: list(_helper(obj))),
        "builtin_tuple": all.ClassHelper(None, lambda obj: tuple(_helper(obj))),
    },
    all.CLASSES_BY_NAME,
)


def mytransverse(obj):
    return all.traverse_and_decode(obj, lambda o: all.decode(o, CUSTOM_CLASSES_BY_NAME))


def dumps(obj):
    return phpserialize.dumps(all.traverse_and_encode(obj, None, CUSTOM_TRAVERSE))


def loads(content):
    obj = phpserialize.loads(content, charset="utf-8", decode_strings=True)
    return mytransverse(obj)


all.register_format("phpserialize", dumps, loads)
