# -*- coding: utf-8 -*-
"""
    serialize.phpserialize
    ~~~~~~~~~~~~~~~~~~~~~~

    Helpers for Pickle Serialization.

    See https://docs.python.org/3/library/pickle.html for more details.

    :copyright: (c) 2016 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""

from collections.abc import MutableMapping

from . import all

try:
    import copyreg
    import pickle
except ImportError:  # pragma: no cover
    all.register_unavailable("pickle", pkg="pickle")
    raise


class DispatchTable(MutableMapping):
    def __getitem__(self, item):
        if item in all.CLASSES:
            return lambda obj: (
                all.CLASSES[item].from_builtin,
                (all.CLASSES[item].to_builtin(obj),),
                None,
                None,
                None,
            )

        return copyreg.dispatch_table[item]  # pragma: no cover

    def __setitem__(self, key, value):  # pragma: no cover
        copyreg.dispatch_table[key] = value

    def __delitem__(self, key):  # pragma: no cover
        del copyreg.dispatch_table[key]

    def __iter__(self):  # pragma: no cover
        return copyreg.dispatch_table.__iter__()

    def __len__(self):  # pragma: no cover
        return copyreg.dispatch_table.__len__()


class MyPickler(pickle.Pickler):

    dispatch_table = DispatchTable()


def dump(obj, fp):
    MyPickler(fp).dump(obj)


def load(fp):
    return pickle.Unpickler(fp).load()


all.register_format("pickle", dumper=dump, loader=load)
