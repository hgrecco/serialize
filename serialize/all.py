# -*- coding: utf-8 -*-
"""
    serialize.all
    ~~~~~~~~~~~~~

    Common routines for serialization and deserialization.

    :copyright: (c) 2016 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""


import pathlib
from collections import namedtuple
from io import BytesIO

#: Stores the functions to convert custom classes to and from builtin types.
ClassHelper = namedtuple("ClassHelper", "to_builtin from_builtin")

#: Stores information and function about each format type.
Format = namedtuple("Format", "extension dump dumps load loads register_class")
UnavailableFormat = namedtuple("UnavailableFormat", "extension msg")

#: Map unavailable formats to the corresponding error message.
# :type: str -> UnavailableFormat
UNAVAILABLE_FORMATS = {}

#: Map available format names to the corresponding dumper and loader.
# :type: str -> Format
FORMATS = {}

#: Map extension to format name.
# :type: str -> str
FORMAT_BY_EXTENSION = {}

#: Map registered classes to the corresponding to_builtin and from_builtin.
# :type: type -> ClassHelper
CLASSES = {}

#: Map class name obtained from str(class) to class.
#: :type: str -> ClassHelper
CLASSES_BY_NAME = {}


def _get_format(fmt):
    """Convenience function to get the format information.

    Raises a nice error if the format is unavailable or unknown.
    """

    if fmt in FORMATS:
        return FORMATS[fmt]

    if fmt in UNAVAILABLE_FORMATS:
        raise ValueError(
            ("'%s' is an unavailable format. " % fmt) + UNAVAILABLE_FORMATS[fmt].msg
        )

    raise ValueError(
        "'%s' is an unknown format. Valid options are %s"
        % (fmt, ", ".join(FORMATS.keys()))
    )


def _get_format_from_ext(ext):
    """Convenience function to get the format information from a file extension.

    Raises a nice error if the extension is unknown.
    """

    ext = ext.lower()
    if ext in FORMAT_BY_EXTENSION:
        return FORMAT_BY_EXTENSION[ext]

    valid = ", ".join(FORMAT_BY_EXTENSION.keys())

    raise ValueError(
        "'%s' is an unknown extension. " "Valid options are %s" % (ext, valid)
    )


def encode_helper(obj, to_builtin):
    """Encode an object into a two element dict using a function
    that can convert it to a builtin data type.
    """

    return dict(__class_name__=str(obj.__class__), __dumped_obj__=to_builtin(obj))


def encode(obj, defaultfunc=None):
    """Encode registered types using the corresponding functions.
    For other types, the defaultfunc will be used
    """

    for klass, (to_builtin, _) in CLASSES.items():
        if isinstance(obj, klass):
            return encode_helper(obj, to_builtin)

    if defaultfunc is None:
        return obj

    return defaultfunc(obj)


def _traverse_dict_ec(obj, ef, td):
    return {
        traverse_and_encode(k, ef, td): traverse_and_encode(v, ef, td)
        for k, v in obj.items()
    }


def _traverse_list_ec(obj, ef, td):
    return [traverse_and_encode(el, ef, td) for el in obj]


def _traverse_tuple_ec(obj, ef, td):
    return tuple(traverse_and_encode(el, ef, td) for el in obj)


DEFAULT_TRAVERSE_EC = {
    dict: _traverse_dict_ec,
    list: _traverse_list_ec,
    tuple: _traverse_tuple_ec,
}


def traverse_and_encode(obj, encode_func=None, trav_dict=None):
    """Transverse a Python data structure encoding each element with encode_func.

    It is used with serialization packages that do not support
    custom types.

    `trav_dict` can be used to provide custom ways of traversing structures.
    """
    encode_func = encode_func or encode
    trav_dict = trav_dict or DEFAULT_TRAVERSE_EC
    for t, func in trav_dict.items():
        if isinstance(obj, t):
            value = func(obj, encode_func, trav_dict)
            break
    else:
        value = encode_func(obj)

    return value


def decode(dct, classes_by_name=None):
    """If the dict contains a __class__ and __serialized__ field tries to
    decode it using the registered classes within the encoder/decoder
    instance.
    """
    if not isinstance(dct, dict):
        return dct

    s = dct.get("__class_name__", None)
    if s is None:
        return dct

    classes_by_name = classes_by_name or CLASSES_BY_NAME
    try:
        _, from_builtin = classes_by_name[s]
        c = dct["__dumped_obj__"]
    except KeyError:
        return dct

    return from_builtin(c)


def _traverse_dict_dc(obj, df, td):
    if "__class_name__" in obj:
        return df(obj)

    return {
        traverse_and_decode(k, df, td): traverse_and_decode(v, df, td)
        for k, v in obj.items()
    }


def _traverse_list_dc(obj, df, td):
    return [traverse_and_decode(el, df, td) for el in obj]


def _traverse_tuple_dc(obj, df, td):
    return tuple(traverse_and_decode(el, df, td) for el in obj)


DEFAULT_TRAVERSE_DC = {
    dict: _traverse_dict_dc,
    list: _traverse_list_dc,
    tuple: _traverse_tuple_dc,
}


def traverse_and_decode(obj, decode_func=None, trav_dict=None):
    """Traverse an arbitrary Python object structure
    calling a callback function for every element in the structure,
    and inserting the return value of the callback as the new value.

    This is used for serialization with libraries that do not have object hooks.
    """
    decode_func = decode_func or decode
    trav_dict = trav_dict or DEFAULT_TRAVERSE_DC
    for t, func in trav_dict.items():
        if isinstance(obj, t):
            value = func(obj, decode_func, trav_dict)
            break
    else:
        value = obj

    return value


# A Sentinel for a missing argument.
MISSING = object()


def register_format(
    fmt,
    dumpser=None,
    loadser=None,
    dumper=None,
    loader=None,
    extension=MISSING,
    register_class=None,
):
    """Register an available serialization format.

    `fmt` is a unique string identifying the format, such as `json`. Use a colon (`:`) to
    separate between subformats.

    `dumpser` and `dumper` should be callables with the same purpose and arguments
    that `json.dumps` and `json.dump`. If one of those is missing, it will be
    generated automatically from the other.

    `loadser` and `loader` should be callables with the same purpose and arguments
    that `json.loads` and `json.load`. If one of those is missing, it will be
    generated automatically from the other.

    `extension` is the file extension used to guess the desired serialization format when loading
    from or dumping to a file. If not given, the part before the colon of `fmt` will be used.
    If `None`, the format will not be associated with any extension.

    `register_class` is a callback made when a class is registered with
    `serialize.register_class`. When a new format is registered,
    previously registered classes are called. It takes on argument, the
    class to register. See `serialize.yaml.py` for an example.
    """

    # For simplicity. We do not allow to overwrite format.
    if fmt in FORMATS:
        raise ValueError("%s is already defined." % fmt)

    # Here we generate register_class if it is not present
    if not register_class:

        def register_class(klass):
            pass

    # Here we generate dumper/dumpser if they are not present.
    if dumper and not dumpser:

        def dumpser(obj):
            buf = BytesIO()
            dumper(obj, buf)
            return buf.getvalue()

    elif not dumper and dumpser:

        def dumper(obj, fp):
            fp.write(dumpser(obj))

    elif not dumper and not dumpser:

        def raiser(*args, **kwargs):
            raise ValueError("dump/dumps is not defined for %s" % fmt)

        dumper = dumpser = raiser

    # Here we generate loader/loadser if they are not present.
    if loader and not loadser:

        def loadser(serialized):
            return loader(BytesIO(serialized))

    elif not loader and loadser:

        def loader(fp):
            return loadser(fp.read())

    elif not loader and not loadser:

        def raiser(*args, **kwargs):
            raise ValueError("load/loads is not defined for %s" % fmt)

        loader = loadser = raiser

    if extension is MISSING:
        extension = fmt.split(":", 1)[0]

    FORMATS[fmt] = Format(extension, dumper, dumpser, loader, loadser, register_class)

    if extension and extension not in FORMAT_BY_EXTENSION:
        FORMAT_BY_EXTENSION[extension.lower()] = fmt

    # register previously registered classes with the new format
    for klass in CLASSES:
        FORMATS[fmt].register_class(klass)


def register_unavailable(fmt, msg="", pkg="", extension=MISSING):
    """Register an unavailable serialization format.

    Unavailable formats are those known by Serialize but that cannot be used
    due to a missing requirement (e.g. the package that does the work).

    """
    if pkg:
        msg = "This serialization format requires the %s package." % pkg

    if extension is MISSING:
        extension = fmt.split(":", 1)[0]

    UNAVAILABLE_FORMATS[fmt] = UnavailableFormat(extension, msg)

    if extension and extension not in FORMAT_BY_EXTENSION:
        FORMAT_BY_EXTENSION[extension.lower()] = fmt


def dumps(obj, fmt):
    """Serialize `obj` to bytes using the format specified by `fmt`"""

    return _get_format(fmt).dumps(obj)


def dump(obj, file, fmt=None):
    """Serialize `obj` to a file using the format specified by `fmt`

    The file can be specified by a file-like object or filename.
    In the latter case the fmt is not need if it can be guessed from the extension.
    """
    if isinstance(file, str):
        file = pathlib.Path(file)

    if isinstance(file, pathlib.Path):
        if fmt is None:
            fmt = _get_format_from_ext(file.suffix.lstrip("."))
        with file.open(mode="wb") as fp:
            dump(obj, fp, fmt)
    else:
        _get_format(fmt).dump(obj, file)


def loads(serialized, fmt):
    """Deserialize bytes using the format specified by `fmt`"""

    return _get_format(fmt).loads(serialized)


def load(file, fmt=None):
    """Deserialize from a file using the format specified by `fmt`

    The file can be specified by a file-like object or filename.
    In the latter case the fmt is not need if it can be guessed from the extension.
    """
    if isinstance(file, str):
        file = pathlib.Path(file)

    if isinstance(file, pathlib.Path):
        if fmt is None:
            fmt = _get_format_from_ext(file.suffix.lstrip("."))
        with file.open(mode="rb") as fp:
            return load(fp, fmt)

    return _get_format(fmt).load(file)


def register_class(klass, to_builtin, from_builtin):
    """Register a custom class for serialization and deserialization.

    `to_builtin` must be a function that takes an object from the custom class
    and returns an object consisting only of Python builtin types.

    `from_builtin` must be a function that takes the output of `to_builtin` and
    returns an object from the custom class.

    In other words:
        >>> obj == from_builtin(to_builtin(obj))
    """
    CLASSES[klass] = CLASSES_BY_NAME[str(klass)] = ClassHelper(to_builtin, from_builtin)
