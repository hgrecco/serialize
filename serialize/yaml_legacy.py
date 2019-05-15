# -*- coding: utf-8 -*-
"""
    serialize.yaml
    ~~~~~~~~~~~~~~

    Helpers for Serpent Serialization.

    See https://pypi.python.org/pypi/pyyaml for more details.

    :copyright: (c) 2016 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""

from . import all

try:
    import yaml
    from yaml.constructor import MappingNode
except ImportError:
    all.register_unavailable('yaml', pkg='pyyaml')
    raise


class Dumper(yaml.Dumper):

    def represent_data(self, data):
        return super().represent_data(all.encode(data))


class Loader(yaml.Loader):

    def construct_object(self, node, deep=False):

        if not isinstance(node, MappingNode):
            return super().construct_object(node, deep)

        dct = super().construct_mapping(node, deep)
        return all.decode(dct)


def dumps(obj):
    return yaml.dump(obj, Dumper=Dumper).encode('utf-8')


def loads(content):
    return yaml.load(content.decode('utf-8'),
                     Loader=Loader)

all.register_format('yaml', dumps, loads)

