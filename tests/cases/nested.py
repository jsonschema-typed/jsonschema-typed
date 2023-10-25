from jsonschema_typed import JSONSchema
from typing import TYPE_CHECKING, Final, Literal, TypedDict, Type


data: JSONSchema["var:jsonschema_typed:dummy_path"] = {"title": "baz"}
awesome: JSONSchema[
    "var:jsonschema_typed:dummy_path", "var:jsonschema_typed:Awesome.key"
]
nested: JSONSchema[
    "schema/nested.json",
    "var:jsonschema_typed:Awesome.key",
    "var:jsonschema_typed:nested",
]

if TYPE_CHECKING:
    reveal_type(data)
    reveal_type(awesome)
    reveal_type(nested)
