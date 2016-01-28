# -*- coding: utf-8 -*-
"""
    serialize.dill
    ~~~~~~~~~~~~~~

    Helpers for Dill Serialization.

    See https://pypi.python.org/pypi/dill for more details.

    :copyright: (c) 2016 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""

from . import all

try:
    import dill
    import copyreg
except ImportError:
    all.register_unavailable('dill', pkg='dill')
    raise


class DispatchTable:

    def __getitem__(self, item):
        if item in all.CLASSES:
            return lambda obj: (all.CLASSES[item].from_builtin,
                                (all.CLASSES[item].to_builtin(obj),),
                                None, None, None)

        return copyreg.dispatch_table[item]

    def __setitem__(self, key, value):
        copyreg.dispatch_table[key] = value

    def get(self, key, default=None):
        if key in all.CLASSES:
            return lambda obj: (all.CLASSES[key].from_builtin,
                                (all.CLASSES[key].to_builtin(obj),),
                                None, None, None)

        return copyreg.dispatch_table.get(key, default)


class MyPickler(dill.Pickler):

    dispatch_table = DispatchTable()


def dump(obj, fp):
    MyPickler(fp).dump(obj)


def load(fp):
    return dill.Unpickler(fp).load()

all.register_format('dill', dumper=dump, loader=load)
