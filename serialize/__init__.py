# -*- coding: utf-8 -*-
"""
    serialize
    ~~~~~~~~~



    :copyright: (c) 2016 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""

from importlib import import_module

try:
    from importlib.metadata import version
except ImportError:
    # Backport for Python < 3.8
    from importlib_metadata import version

try:  # pragma: no cover
    __version__ = version("serialize")
except Exception:  # pragma: no cover
    # we seem to have a local copy not installed without setuptools
    # so the reported version will be unknown
    __version__ = "unknown"


# Modules that help serialize use other packages.

_MODULES = (
    "bson",
    "dill",
    "json",
    "msgpack",
    "phpserialize",
    "pickle",
    "serpent",
    "yaml",
    "yaml_legacy",
)

for name in _MODULES:
    try:
        import_module("." + name, "serialize")
    except Exception:
        pass

# Others to consider in the future for specialized serialization:
# CSV, pandas.DATAFRAMES, hickle, hdf5

from .all import dump, dumps, load, loads, register_class  # noqa: E402

__all__ = ["dump", "dumps", "load", "loads", "register_class"]
