[![PyPI version](https://img.shields.io/pypi/v/jsonschema-typed.svg?logo=pypi&logoColor=FFE873)](https://pypi.org/project/jsonschema-typed/)
[![Python version](https://img.shields.io/pypi/pyversions/jsonschema-typed)](https://pypi.org/project/jsonschema-typed/)
[![PyPI downloads](https://img.shields.io/pypi/dm/jsonschema-typed)](https://pypistats.org/packages/jsonschema-typed)
[![License](https://img.shields.io/pypi/l/jsonschema-typed)](LICENSE)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# JSON Schema-powered type annotations

This package provides a way to automatically produce type annotations based
on [`jsonschema`-schemas](https://json-schema.org).

Not all concepts covered by `jsonschema` are expressible within Python typing annotations. However, most things
will work like you'd expect. Most types are translated trivially
(`integer`, `number`, `string`, `array`, `boolean` and `null`).
The interesting type is `object`, which is translated into a [``TypedDict``](https://www.python.org/dev/peps/pep-0589/).

**Warning:** This is based on the [mypy plugin system](https://mypy.readthedocs.io/en/latest/extending_mypy.html), which
is stated to have no backwards compatibility guarantee. New versions of mypy might not be supported immediately.

## Example

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

from typing import TYPE_CHECKING
from jsonschema_typed import JSONSchema

data: JSONSchema["path/to/schema.json"] = {"title": "baz"}

if TYPE_CHECKING:
    reveal_type(data)  # Revealed type is 'TypedDict('FooSchema', {'title': builtins.str,
                       #                                           'awesome'?: Union[builtins.int, builtins.float]})'
data["description"] = "there is no description"  # TypedDict "FooSchema" has no key 'description'
data["awesome"] = 42
data["awesome"] = None  # Argument 2 has incompatible type "None"; expected "Union[int, float]"
```

You can also get types of parts of a schema, as well as types of elements in arrays, e.g.:

```python
subschema: JSONSchema['schema/myschema.json', 'keyname1', 'keyname2']
schema: JSONSchema['var:modulename:variablename']
```

Take a look at the [test cases](tests/cases) for more usage examples.

## Installation

```bash
pip install jsonschema-typed
```

You also need to enable the plugin(s) in your `mypy.ini` configuration file:

```toml
# mypy.ini
[mypy]
plugins = jsonschema_typed.plugin, jsonschema_typed.optional_typed_dict

# Due to a quirk of how these type hints are generated, mypy's caching breaks.
# Disabling caching might be required.
cache_dir = /dev/null
```

## Requirements

The above installations resolves the dependencies, which consist of `mypy` and `jsonschema` (naturally).
Testing has been done with versions:

- mypy==0.761
- jsonschema==3.2.0

Probably some older versions will also work. Report an [issue](https://github.com/jsonschema-typed/jsonschema-typed/issues)
if you need other versions.

## Limitations

- `additionalProperties` doesn't really have an equivalent in TypedDict.
- The ``default`` keyword is not supported; but see: https://github.com/python/mypy/issues/6131.
- Self-references (e.g. ``"#"``) can't really work properly until nested
  forward-references are supported; see: https://github.com/python/mypy/issues/731.
