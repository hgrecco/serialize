# -*- coding: utf-8 -*-
"""
    serialize.dill
    ~~~~~~~~~~~~~~

    Helpers for Dill Serialization.

    See https://pypi.python.org/pypi/dill for more details.

    :copyright: (c) 2016 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""

from . import all, pickle

try:
    import dill
except ImportError:
    all.register_unavailable("dill", pkg="dill")
    raise


class MyPickler(dill.Pickler):

    dispatch_table = pickle.DispatchTable()


def dump(obj, fp):
    MyPickler(fp).dump(obj)


def load(fp):
    return dill.Unpickler(fp).load()


all.register_format("dill", dumper=dump, loader=load)
