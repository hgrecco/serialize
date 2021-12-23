# -*- coding: utf-8 -*-
"""
    serialize.dill
    ~~~~~~~~~~~~~~

    Helpers for JSON Serialization.

    See https://docs.python.org/3/library/json.html for more details.

    :copyright: (c) 2016 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""

from . import all

try:
    import json
except ImportError:  # pragma: no cover
    all.register_unavailable("json", pkg="json")
    raise


class Encoder(json.JSONEncoder):
    def default(self, obj):
        return all.encode(obj, super().default)


def dumps(obj):
    return json.dumps(obj, cls=Encoder).encode("utf-8")


def dumps_pretty(obj):
    return json.dumps(
        obj, cls=Encoder, sort_keys=True, indent=4, separators=(",", ": ")
    ).encode("utf-8")


def loads(content):
    return json.loads(content.decode("utf-8"), object_hook=all.decode)


# We create two different subformats for json.
# The first (default) is compact, the second is pretty.

all.register_format("json", dumps, loads)
all.register_format("json:pretty", dumps_pretty, loads)
