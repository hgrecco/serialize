

from unittest import TestCase


from serialize import register_class, loads, dumps

from serialize.all import FORMATS, UNAVAILABLE_FORMATS


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


class TestAllAvailable(TestCase):

    def test_available(self):
        self.assertFalse(UNAVAILABLE_FORMATS)


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
        self.assertEqual(obj, loads(dumps(obj, self.FMT), self.FMT))

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


for key in FORMATS.keys():
    name = "TestEncoderDecoder_%s" % key
    globals()[name] = type(name,
                           (_TestEncoderDecoder, TestCase),
                           dict(FMT=key))
