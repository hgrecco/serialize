# -*- coding: utf-8 -*-
"""
    serialize.simplejson
    ~~~~~~~~~~~~~~~~~~~~

    Helpers for JSON Serialization.

    See https://github.com/simplejson/simplejson for more details.

    :copyright: (c) 2016 by Hernan E. Grecco, Pieter T. Eendebak
    :license: BSD, see LICENSE for more details.
"""

from . import all
from .all import _traverse_dict_ec, _traverse_list_ec

try:
    import simplejson as json
except ImportError:  # pragma: no cover
    all.register_unavailable("simplejson", pkg="simplejson")
    raise


class Encoder(json.JSONEncoder):
    def default(self, obj):
        return all.encode(obj, super().default)


def _traverse_tuple_ec(obj, ef, td):
    return {
        "__class_name__": "tuple",
        "__dumped_obj": list(all.traverse_and_encode(el, ef, td) for el in obj),
    }


trav_dict = {
    dict: _traverse_dict_ec,
    list: _traverse_list_ec,
    tuple: _traverse_tuple_ec,
}


def df(obj):
    """Decode function that handles encoded tuples"""
    if obj["__class_name__"] == "tuple":
        return tuple(obj["__dumped_obj"])
    else:
        return obj["__dumped_obj"]


def dumps(obj):
    return json.dumps(
        all.traverse_and_encode(obj, trav_dict=trav_dict),
        cls=Encoder,
        tuple_as_array=True,
    ).encode("utf-8")


def dumps_pretty(obj):
    return json.dumps(
        all.traverse_and_encode(obj, trav_dict=trav_dict),
        cls=Encoder,
        sort_keys=True,
        tuple_as_array=True,
        indent=4,
        separators=(",", ": "),
    ).encode("utf-8")


def loads(content):
    obj = json.loads(content.decode("utf-8"), object_hook=all.decode)
    return all.traverse_and_decode(obj, decode_func=df)


# We create two different subformats for json.
# The first (default) is compact, the second is pretty.

all.register_format("simplejson", dumps, loads)
all.register_format("simplejson:pretty", dumps_pretty, loads)
