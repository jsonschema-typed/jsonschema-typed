# JSON Schema-powered type annotations

The goal of this project is to use JSON Schema for type checking in Python.

While there is not a perfect 1:1 mapping between concepts in JSON Schema and
Python's typing system, there is enough of an isomorphism to warrant some
exploration of the possibilities. Since a JSON document is generally
represented as a ``dict`` in Python programs, this project looks specifically
at interpreting JSON schema as
[``TypedDict``](https://www.python.org/dev/peps/pep-0589/) definitions.

**Warning:** there are bound to be some abuses of the [mypy plugin
system](https://mypy.readthedocs.io/en/latest/extending_mypy.html) here. You
have been warned.

This leverages (and is inspired by) https://github.com/Julian/jsonschema.

## Overview

A JSON schema:

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "http://foo.qwerty/some/schema#",
    "title": "Foo Schema",
    "type": "object",
    "properties": {
        "title": {
            "type": "string"
        },
        "awesome": {
            "type": "number"
        }
    },
    "required": ["title"]
}
```

A TypedDict:

```python
from jsonschema_typed.types import JSONSchema

data: JSONSchema['path/to/schema.json'] = dict(title='baz')
data['description'] = 'there is no description'  # TypedDict "FooSchema" has no key 'description'
data['awesome'] = 42
data['awesome'] = None  # Argument 2 has incompatible type "None"; expected "Union[int, float]"
```

## Installation

```bash
pip install jsonschema-typed
```

or

```bash
git clone git@github.com:erickpeirson/jsonschema-typed.git
cd jsonschema-typed
python setup.py install
```

## Requirements

So far I have only tried this with:

- mypy==0.701
- jsonschema==3.0.1

But probably older versions work. You could try it out and
[let me know](https://github.com/erickpeirson/jsonschema-typed/issues).

## Limitations

- ``additionalProperties`` doesn't really have an equivalent in TypedDict. Yet.
- Cases in which the root of the schema is anything other than an ``object``
  are not terribly interesting for this project, so we ignore them for now.
  Array values for ``type`` (e.g. ``"type": ["object", "boolean"]``) are
  otherwise supported with ``Union``.
- The ``default`` keyword is not supported; but see:
   https://github.com/python/mypy/issues/6131.
- Self-references (e.g. ``"#"``) can't really work properly until nested
  forward-references are supported; see
  https://github.com/python/mypy/issues/731.

There are probably others.


## Approach

So far two approaches are attempted:

1. Annotating a ``dict`` instance that will be a ``TypedDict`` that conforms to
   the JSON Schema (as best we can enforce it).
2. Using a dynamic base class that is typed as a ``TypedDict``.

Both examples below use the schema:

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "http://foo.qwerty/some/schema#",
    "title": "Foo Schema",
    "type": "object",
    "properties": {
        "title": {
            "type": "string"
        },
        "awesome": {
            "type": "number"
        }
    }
}
```


### First approach: annotating a ``dict``

This has the advantage of being fairly simple. It is implemented via
``jsonschema_typed.plugin.JSONSchemaPlugin.get_type_analyze_hook``.

```python
from jsonschema_typed.types import JSONSchema

data: JSONSchema['path/to/schema.json'] = dict(title='baz')
reveal_type(data)  # Revealed type is 'TypedDict('FooSchema', {'title'?: builtins.str, 'awesome'?: Union[builtins.int, builtins.float]})'
data['description'] = 'there is no description'  # TypedDict "FooSchema" has no key 'description'
data['awesome'] = 42
data['awesome'] = None  # Argument 2 has incompatible type "None"; expected "Union[int, float]"
```

Here is the mypy output:

```
main.py:4: error: Revealed type is 'TypedDict('FooSchema', {'title'?: builtins.str, 'awesome'?: Union[builtins.int, builtins.float]})'
main.py:5: error: TypedDict "FooSchema" has no key 'description'
main.py:7: error: Argument 2 has incompatible type "None"; expected "Union[int, float]"
```

Note that the right-hand side can be a ``dict`` or a subclass of ``dict``, so
you could define a subclass like:

```python
class Foo(dict):
    """Some domain logic on your object."""

    def do_something(self, arg: int) -> int:
        """Do something awesome."""
        return arg * self['awesome']

data: JSONSchema['schema/test.json'] = Foo(title='baz')
reveal_type(data)  # Revealed type is 'TypedDict('FooSchema', {'title'?: builtins.str, 'awesome'?: Union[builtins.int, builtins.float]})'
data['description'] = 'there is no description'  # TypedDict "FooSchema" has no key 'description'
data['awesome'] = 42
data['awesome'] = None  # Argument 2 has incompatible type "None"; expected "Union[int, float]"
```

Of course this isn't quite consistent with PEP-589 which
[states](https://www.python.org/dev/peps/pep-0589/#class-based-syntax) that:

> Methods are not allowed, since the runtime type of a TypedDict object will
> always be just dict (it is never a subclass of dict).

So use at your own risk.

### Second approach: dynamic base class

This has the advantage of being able to add some runtime-functionality, e.g.
use ``jsonschema`` to actually validate data at runtime. It is implemented via
``jsonschema_typed.plugin.JSONSchemaPlugin.get_dynamic_class_hook``.

But again, this isn't quite consistent with PEP-589 which
[states](https://www.python.org/dev/peps/pep-0589/#class-based-syntax), so
use at your own risk.

```python
from jsonschema_typed.types import JSONSchemaBase


Base = JSONSchemaBase('path/to/schema.json')

class Foo(Base):
    """All your base in one place."""

    def do_something(self, arg: int) -> int:
        """Do something awesome."""
        return arg * self['awesome']


data = Foo(title='baz')
reveal_type(data)  # Revealed type is 'TypedDict('FooSchema', {'title'?: builtins.str, 'awesome'?: Union[builtins.int, builtins.float]})'
data['description'] = 'there is no description'  # TypedDict "FooSchema" has no key 'description'
data['awesome'] = 42
data['awesome'] = None  # Argument 2 has incompatible type "None"; expected "Union[int, float]"
```

## TODO

- [ ] Decide whether to stick with just one approach (and which one)
- [ ] Write some tests
- [ ] Test against other versions of mypy + jsonschema
