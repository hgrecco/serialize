
import io
import os
from unittest import TestCase, skipIf

from serialize import register_class, loads, dumps, load, dump
from serialize.all import (FORMATS, UNAVAILABLE_FORMATS,
                           _get_format_from_ext, _get_format,
                           register_format)


class X:

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __eq__(self, other):
        if not self.__class__ is other.__class__:
            return False
        if self.a != other.a:
            return False
        if self.b != other.b:
            return False
        return True

    def __str__(self):
        return 'X(%s, %s)' % (self.a, self.b)

    __repr__ = __str__


def to_builtin(obj):
    return obj.a, obj.b


def from_builtin(content):
    return X(content[0], content[1])


register_class(X, to_builtin, from_builtin)

register_format('_test')


class TestAvailable(TestCase):

    @skipIf(os.environ.get('EXTRAS', None) == 'N', 'Extras not installed')
    def test_available(self):
        self.assertFalse(UNAVAILABLE_FORMATS)

    def test_unknown_format(self):
        self.assertRaises(ValueError, dumps, 'hello', 'dummy_format')
        self.assertRaises(ValueError, _get_format_from_ext, 'dummy_format')

    def test_no_replace(self):
        self.assertRaises(ValueError, register_format, '_test')

    def test_no_dumper_no_loader(self):
        self.assertRaises(ValueError, dumps, 'hello', '_test')
        self.assertRaises(ValueError, loads, 'hello', '_test')
        buf = io.BytesIO()
        self.assertRaises(ValueError, dump, 'hello', buf, 'test')
        self.assertRaises(ValueError, load, buf, 'test')

NESTED_DICT = {
        "level1_1": {
            "level2_1": [1, 2, 3],
            "level2_2": [4, 5, 6]
        },
        "level1_2": {
            "level2_1": [1, 2, 3],
            "level2_2": [4, 5, 6]
        },
        "level1_3": {
            "level2_1": {
                "level3_1": [1, 2, 3],
                "level3_2": [4, 5, 6]
            },
            "level2_2": [4, 5, 6]
        }
    }


class _TestEncoderDecoder:

    FMT = None

    def _test_round_trip(self, obj):

        dumped = dumps(obj, self.FMT)

        # dumps / loads
        self.assertEqual(obj, loads(dumped, self.FMT))

        buf = io.BytesIO()
        dump(obj, buf, self.FMT)

        # dump / dumps
        self.assertEqual(dumped, buf.getvalue())

        buf.seek(0)
        # dump / load
        self.assertEqual(obj, load(buf, self.FMT))

    def test_file_by_name(self):
        fh = _get_format(self.FMT)
        obj = dict(answer=42)

        filename1 = 'tmp.' + fh.extension
        dump(obj, filename1)
        try:
            obj1 = load(filename1)
            self.assertEqual(obj, obj1)
        finally:
            os.remove(filename1)

        filename2 = 'tmp.' + fh.extension + '.bla'
        dump(obj, filename2, fmt=self.FMT)
        try:
            obj2 = load(filename2, fmt=self.FMT)
            self.assertEqual(obj, obj2)
        finally:
            os.remove(filename2)

    def test_format_from_ext(self):
        if ':' in self.FMT:
            return
        fh = FORMATS[self.FMT]
        self.assertEqual(_get_format_from_ext(fh.extension), self.FMT)

    def test_response_bytes(self):

        obj = 'here I am'

        self.assertIsInstance(dumps(obj, self.FMT), bytes)

    def test_simple_types(self):
        self._test_round_trip('hello')
        self._test_round_trip(1)
        self._test_round_trip(1.1)
        self._test_round_trip(None)
        self._test_round_trip(True)
        self._test_round_trip(False)

    def test_dict(self):
        self._test_round_trip(dict())
        self._test_round_trip(dict(x=1, y=2, z=3))

    def test_list(self):
        self._test_round_trip([])
        self._test_round_trip([1, 2, 3])

    def test_nest_type(self):
        self._test_round_trip(NESTED_DICT)

    def test_custom_object(self):

        c = X(3, 4)
        self._test_round_trip(c)

    def test_custom_object_in_container(self):

        c = dict(a=X(3, 4), b=X(1, 2), d=[X(0, 1), X(2, 3)])
        self._test_round_trip(c)


class _TestUnavailable:

    def test_raise(self):
        self.assertRaises(ValueError, dumps, 'hello', self.FMT)

    def test_raise_from_ext(self):
        self.assertRaises(ValueError, dumps, 'hello', self.FMT)


for key in FORMATS.keys():
    if key.startswith('_test'):
        continue
    name = "TestEncoderDecoder_%s" % key.replace(':', '_')
    globals()[name] = type(name,
                           (_TestEncoderDecoder, TestCase),
                           dict(FMT=key))

for key in UNAVAILABLE_FORMATS.keys():
    if key.startswith('_test'):
        continue
    name = "TestEncoderDecoder_%s" % key
    globals()[name] = type(name,
                           (_TestUnavailable, TestCase),
                           dict(FMT=key))
