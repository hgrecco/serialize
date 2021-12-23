.. image:: https://img.shields.io/pypi/v/serialize.svg
    :target: https://pypi.python.org/pypi/serialize
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/l/serialize.svg
    :target: https://pypi.python.org/pypi/serialize
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/serialize.svg
    :target: https://pypi.python.org/pypi/serialize
    :alt: Python Versions

.. image:: https://github.com/hgrecco/serialize/workflows/CI/badge.svg
    :target: https://github.com/hgrecco/serialize/actions?query=workflow%3ACI
    :alt: CI

.. image:: https://github.com/hgrecco/serialize/workflows/Lint/badge.svg
    :target: https://github.com/hgrecco/serialize/actions?query=workflow%3ALint
    :alt: LINTER


.. image:: https://coveralls.io/repos/github/hgrecco/serialize/badge.svg?branch=master
    :target: https://coveralls.io/github/hgrecco/serialize?branch=master
    :alt: Coverage


Serialize: A common Python API for multiple serialization formats
=================================================================

::

    There are multiple serialization formats out there ...
        ... and great packages to use them.

But they all have a different API and switching among them is not so simple
as it should be. Serialize helps you to do it, including dealing with custom
classes. Let's dump a dict using the `pickle` format:

.. code-block:: python

    >>> from serialize import dumps, loads
    >>> dumps(dict(answer=42), fmt='pickle')
    b'\x80\x03}q\x00X\x06\x00\x00\x00answerq\x01K*s.'
    >>> loads(_, fmt='pickle')
    {'answer': 42}

And here comes the cool thing, you can just change the serialization format
without having to learn a new API. Let's now dump it using msgpack:

.. code-block:: python

    >>> dumps(dict(answer=42), fmt='msgpack')
    b'\x81\xa6answer*'
    >>> loads(_, fmt='msgpack')
    {'answer': 42}

Serialize currently support 8 different formats: `bson`, `dill`, `json` (builtin or with simplejson package), `msgpack`,
`phpserialize`, `pickle`, `serpent` and `yaml`. Serialize does not implement these
formats but rather relies on established, well tested packages. If they are installed,
serialize will use them.

::

     ** Serialize allows you to use them all with the same API! **


You can also use the `dump` and `load` to write directly to file-like object:

.. code-block:: python

    >>> from serialize import dump, load
    >>> with open('output.yaml', 'wb') as fp:
    ...     dump(dict(answer=42), fp, fmt='yaml')
    >>> with open('output.yaml', 'rb') as fp:
    ...     load(fp, fmt='yaml')
    {'answer': 42}

or use directly the filename and the format will be inferred:

.. code-block:: python

    >>> dump(dict(answer=42), 'output.yaml')
    >>> load('output.yaml')
    {'answer': 42}

A very common case is to dump and load objects from custom classes such as:

.. code-block:: python

    >>> class User:
    ...     def __init__(self, name, age):
    ...         self.name = name
    ...         self.age = age
    ...
    >>> john = User('John Smith', 27)


But some serialization packages do not support this important feature and the
rest usually have very different API between them. Serialize provides
you a common, simple interface for this. You just need to define a function
that is able to convert the object to an instance of a builtin type and the
converse:

.. code-block:: python

    >>> from serialize import register_class
    >>> def user_to_builtin(u):
    ...     return (u.name, u.age)
    ...
    >>> def user_from_builtin(c):
    ...     return User(c[0], c[1])
    ...

    >>> register_class(User, user_to_builtin, user_from_builtin)


And that's all. You can then use it directly without any hassle:

.. code-block:: python

    >>> dumps(john, fmt='bson')
    b"y\x00\x00\x00\x03__bson_follow__\x00c\x00\x00\x00\x04__dumped_obj__
    \x00\x1e\x00\x00\x00\x020\x00\x0b\x00\x00\x00John Smith\x00\x101\x00
    \x1b\x00\x00\x00\x00\x02__class_name__\x00\x1c\x00\x00\x00<class '__m
    ain__.Username'>\x00\x00\x00"
    >>> v = loads(_, fmt='bson')
    >>> v.name
    'John Smith'
    >>> v.age
    27


Enjoy!

