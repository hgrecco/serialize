# -*- coding: utf-8 -*-
"""
    serialize.yaml
    ~~~~~~~~~~~~~~

    Helpers for YAML Serialization.

    See https://pypi.python.org/pypi/pyyaml for more details.

    :copyright: (c) 2021 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""

from . import all

try:
    import yaml
    from yaml.constructor import MappingNode
except ImportError:
    all.register_unavailable("yaml", pkg="pyyaml")
    raise


# Note: these tags a global namespace, so we need a unique URL/tag to use here.
#
# Pyyaml uses "tag:yaml.org,2002:...", some of which are defined by
# yaml.org/spec/..., but the python-specific ones (like python/tuple,
# python/complex, etc) seem to be their own, and probably should have used the
# hostname pyyaml.org. Serialize's github homepage ought to be a pretty stable
# URL we can use.
SERIALIZED_TAG = "tag:github.com/hgrecco/serialize,2019:python/serialize-encode"


class Dumper(yaml.Dumper):
    def represent_serialized(self, data):
        return self.represent_mapping(SERIALIZED_TAG, all.encode(data))


class Loader(yaml.Loader):
    def construct_serialized(self, node):
        assert node.tag == SERIALIZED_TAG
        assert isinstance(node, MappingNode)
        dct = self.construct_mapping(node, deep=True)
        return all.decode(dct)


def dumps(obj):
    return yaml.dump(obj, Dumper=Dumper).encode("utf-8")


def loads(content):
    return yaml.load(content.decode("utf-8"), Loader=Loader)


def _register_class(klass):
    Dumper.add_representer(klass, Dumper.represent_serialized)

    Loader.add_constructor(SERIALIZED_TAG, Loader.construct_serialized)


all.register_format("yaml", dumps, loads, register_class=_register_class)
