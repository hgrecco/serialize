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

try:
    import simplejson as json
except ImportError:  # pragma: no cover
    all.register_unavailable('simplejson', pkg='simplejson')
    raise


class Encoder(json.JSONEncoder):

    def default(self, obj):
        return all.encode(obj, super().default)


def dumps(obj):
    return json.dumps(obj, cls=Encoder, tuple_as_array=False).encode('utf-8')


def dumps_pretty(obj):
    return json.dumps(obj, cls=Encoder, sort_keys=True, tuple_as_array=False,
                      indent=4, separators=(',', ': ')).encode('utf-8')


def loads(content):
    return json.loads(content.decode('utf-8'),
                      object_hook=all.decode)


# We create two different subformats for json.
# The first (default) is compact, the second is pretty.

all.register_format('simplejson', dumps, loads)
all.register_format('simplejson:pretty', dumps_pretty, loads)
