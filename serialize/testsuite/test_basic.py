
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

OBJECT_STATE = ('This', 'Is', 2, 'Object', u'State')
OBJECT_MEMBERS = ('These', 'are', ('object', 'members'))
class Reduce_x(dict):
    def __init__(self, *args, **kwargs):
        try:
            super(Reduce_x, self).__init__(*args, **kwargs)
        except:
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
        return (
            self.__class__,
            self._initargs())

class Reduce_3(Reduce_x):
    def __reduce__(self):
        return (
            self.__class__,
            self._initargs(),
            self._getstate())

class Reduce_4(Reduce_x):
    def __reduce__(self):
        return (
            self.__class__,
            self._initargs(),
            self._getstate(),
            iter(OBJECT_MEMBERS))

class Reduce_5(Reduce_x):
    def __reduce__(self):
        return (
            self.__class__,
            self._initargs(),
            self._getstate(),
            iter(OBJECT_MEMBERS),
            zip(self.keys(), self.values()))


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

    def test_reduce_string(self):
        # Most formats don't support this (pickle does)
        if self.FMT in [
                        'yaml:legacy',
                        'json',
                        'serpent',
                        'phpserialize',
                        'msgpack',
                        'json:pretty',
                        'bson',
                        'yaml' # https://github.com/yaml/pyyaml/issues/300
                        ]:
            return
        self._test_round_trip(GLOBAL_X)
        self._test_round_trip(GLOBAL_Y)

    def test_reduce(self):
        # yaml:legacy exists because it did not handle these case, so skip these tests
        if self.FMT == 'yaml:legacy':
            return
        classes = [Reduce_2, Reduce_3, Reduce_4, Reduce_5]
        for clsa in classes:
            a = clsa(a=1,b=2,c=dict(d=3,e=4))
            self._test_round_trip(a)

            for clsb in classes:
                b = clsb(f=8,g=9,h=dict(i=9,j=10))
                a['B'] = b
                self._test_round_trip(b)


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
