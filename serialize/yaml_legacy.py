# -*- coding: utf-8 -*-
"""
    serialize.yaml_legacy
    ~~~~~~~~~~~~~~~~~~~~~

    Helpers for YAML Serialization.

    See https://pypi.python.org/pypi/pyyaml for more details.

    :copyright: (c) 2016 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""

from . import all

try:
    import yaml
    from yaml.constructor import MappingNode
except ImportError:
    all.register_unavailable("yaml:legacy", pkg="pyyaml")
    raise


class Dumper(yaml.Dumper):
    def represent_data(self, data):
        return super().represent_data(all.encode(data))


class Loader(yaml.Loader):
    def construct_object(self, node, deep=False):

        # It seems that pyyaml is changing the internal structure of the node
        tmp = super().construct_object(node, deep)

        if isinstance(node, MappingNode):
            dct = super().construct_mapping(node, deep)
            decoded = all.decode(dct)
            if decoded is not dct:
                return decoded

        return tmp


def dumps(obj):
    return yaml.dump(obj, Dumper=Dumper).encode("utf-8")


def loads(content):
    return yaml.load(content.decode("utf-8"), Loader=Loader)


all.register_format("yaml:legacy", dumps, loads)
