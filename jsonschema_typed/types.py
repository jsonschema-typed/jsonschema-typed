"""
The jsonschema_typed library provides a single type definition, `JSONSchema`.

Please note that at runtime, this type is only an alias to `typing.Type`, and
does not hold any relevant properties or information. The type has special behaviour
only to mypy after the plugin has been installed and enabled. This means that the type
should not be used in any context other than for annotations.
"""
