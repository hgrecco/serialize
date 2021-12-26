import io
import os
import pathlib

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


@pytest.mark.parametrize("obj", VALUES)
@pytest.mark.parametrize("fmt", FORMATS)
def test_round_trip(obj, fmt):
    if fmt == "_test":
        return
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
