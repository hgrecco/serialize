import io
import os
import pathlib
import sys

import pytest

from serialize import dump, dumps, load, loads, register_class
from serialize.all import (
    FORMATS,
    UNAVAILABLE_FORMATS,
    _get_format,
    _get_format_from_ext,
    register_format,
)


class X:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return False
        if self.a != other.a:
            return False
        if self.b != other.b:
            return False
        return True

    def __str__(self):
        return "X(%s, %s)" % (self.a, self.b)

    __repr__ = __str__


def to_builtin(obj):
    return obj.a, obj.b


def from_builtin(content):
    return X(content[0], content[1])


register_class(X, to_builtin, from_builtin)


@pytest.mark.parametrize("fmt", FORMATS)
def test_available(fmt):
    assert fmt not in UNAVAILABLE_FORMATS


def test_unknown_format():
    with pytest.raises(ValueError):
        _get_format_from_ext("dummy_format")

    with pytest.raises(ValueError):
        dumps("hello", "dummy_format")


NESTED_DICT = {
    "level1_1": {"level2_1": [1, 2, 3], "level2_2": [4, 5, 6]},
    "level1_2": {"level2_1": [1, 2, 3], "level2_2": [4, 5, 6]},
    "level1_3": {
        "level2_1": {"level3_1": [1, 2, 3], "level3_2": [4, 5, 6]},
        "level2_2": [4, 5, 6],
    },
}


VALUES = [
    "hello",
    1,
    1.2,
    None,
    True,
    False,
    dict(),
    dict(x=1, y=2, z=3),
    [],
    [1, 2, 3],
    NESTED_DICT,
    X(3, 4),
    dict(a=X(3, 4), b=X(1, 2), d=[X(0, 1), X(2, 3)]),
]


def _test_round_trip(obj, fmt):
    dumped = dumps(obj, fmt)

    # dumps / loads
    assert obj == loads(dumped, fmt)

    buf = io.BytesIO()
    dump(obj, buf, fmt)

    # dump / dumps
    assert dumped == buf.getvalue()

    buf.seek(0)
    # dump / load
    assert obj == load(buf, fmt)


@pytest.mark.parametrize("obj", VALUES)
@pytest.mark.parametrize("fmt", FORMATS)
def test_round_trip(obj, fmt):
    if fmt == "_test":
        return

    with pytest.warns(None) as record:
        _test_round_trip(obj, fmt)

    assert len(record) == 0


@pytest.mark.parametrize("fmt", FORMATS)
def test_file_by_name(fmt):
    if fmt == "_test":
        return
    fh = _get_format(fmt)
    obj = dict(answer=42)

    filename1 = "tmp." + fh.extension

    try:
        dump(obj, filename1)
        obj1 = load(filename1)
        assert obj == obj1
    finally:
        os.remove(filename1)

    filename2 = "tmp." + fh.extension + ".bla"

    try:
        dump(obj, filename2, fmt=fmt)
        obj2 = load(filename2, fmt=fmt)
        assert obj == obj2
    finally:
        os.remove(filename2)


@pytest.mark.parametrize("fmt", FORMATS)
def test_file_by_name_pathlib(fmt):
    if fmt == "_test":
        return
    fh = _get_format(fmt)
    obj = dict(answer=42)

    filename1 = "tmp." + fh.extension
    filename1 = pathlib.Path(filename1)

    try:
        dump(obj, filename1)
        obj1 = load(filename1)
        assert obj == obj1
    finally:
        filename1.unlink()

    filename2 = "tmp." + fh.extension + ".bla"
    filename2 = pathlib.Path(filename2)
    try:
        dump(obj, filename2, fmt=fmt)
        obj2 = load(filename2, fmt=fmt)
        assert obj == obj2
    finally:
        filename2.unlink()


@pytest.mark.parametrize("fmt", FORMATS)
def test_format_from_ext(fmt):
    if fmt == "_test":
        return
    if ":" in fmt:
        return
    fh = FORMATS[fmt]
    assert _get_format_from_ext(fh.extension) == fmt


@pytest.mark.parametrize("fmt", FORMATS)
def test_response_bytes(fmt):
    if fmt == "_test":
        return
    obj = "here I am"

    assert isinstance(dumps(obj, fmt), bytes)


register_format("_test")


def test_no_replace():
    with pytest.raises(ValueError):
        register_format("_test")


def test_no_dumper_no_loader():
    with pytest.raises(ValueError):
        dumps("hello", "_test")

    with pytest.raises(ValueError):
        loads("hello", "_test")

    buf = io.BytesIO()
    with pytest.raises(ValueError):
        dump("hello", buf, "test")

    buf = io.BytesIO()
    with pytest.raises(ValueError):
        load(buf, "test")


#
# Some classes that exercise various parts of pickle's __reduce__() protocol
#
class Reduce_string(object):
    def __reduce__(self):
        if self is GLOBAL_X:
            return "GLOBAL_X"
        elif self is GLOBAL_Y:
            return "GLOBAL_Y"
        else:
            raise Exception("Unknown Reduce_string()")


GLOBAL_X = Reduce_string()
GLOBAL_Y = Reduce_string()

OBJECT_STATE = ("This", "Is", 2, "Object", u"State")
OBJECT_MEMBERS = ("These", "are", ("object", "members"))


class Reduce_x(dict):
    def __init__(self, *args, **kwargs):
        try:
            super(Reduce_x, self).__init__(*args, **kwargs)
        except Exception:
            raise Exception(repr(args))
        self.__dict__ = self

    def extend(self, *args):
        assert tuple(*args) == OBJECT_MEMBERS

    def __setstate__(self, state):
        # State should already have been initialized via __init__, just check
        # for roundtrip
        assert state == OBJECT_STATE

    def _getstate(self):
        # State should already have been initialized via __init__, just check
        # for roundtrip
        return OBJECT_STATE

    def __setitem__(self, key, value):
        # State should already have been initialized via __init__, just check
        # for roundtrip
        if key in self:
            assert self[key] == value
        super(Reduce_x, self).__setitem__(key, value)

    def _initargs(self):
        args = list(zip(self.keys(), self.values()))
        return (args,)


class Reduce_2(Reduce_x):
    def __reduce__(self):
        return (self.__class__, self._initargs())


class Reduce_3(Reduce_x):
    def __reduce__(self):
        return (self.__class__, self._initargs(), self._getstate())


class Reduce_4(Reduce_x):
    def __reduce__(self):
        return (
            self.__class__,
            self._initargs(),
            self._getstate(),
            iter(OBJECT_MEMBERS),
        )


class Reduce_5(Reduce_x):
    def __reduce__(self):
        return (
            self.__class__,
            self._initargs(),
            self._getstate(),
            iter(OBJECT_MEMBERS),
            zip(self.keys(), self.values()),
        )


@pytest.mark.parametrize("fmt", ["pickle"])
def test_reduce_string(fmt):
    # Most formats don't support this (pickle does)
    _test_round_trip(GLOBAL_X, fmt)
    _test_round_trip(GLOBAL_Y, fmt)


@pytest.mark.parametrize("fmt", FORMATS)
@pytest.mark.parametrize("klass1", [Reduce_2, Reduce_3, Reduce_4, Reduce_5])
@pytest.mark.parametrize("klass2", [Reduce_2, Reduce_3, Reduce_4, Reduce_5])
@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
def test_reduce(fmt, klass1, klass2):
    # yaml:legacy exists because it did not handle these case, so skip these tests
    if fmt == "yaml:legacy" or fmt == "_test":
        return

    a = klass1(a=1, b=2, c=dict(d=3, e=4))
    _test_round_trip(a, fmt)

    b = klass2(f=8, g=9, h=dict(i=9, j=10))
    a["B"] = b
    _test_round_trip(b, fmt)
