from typing import TYPE_CHECKING

from jsonschema_typed import JSONSchema

array: JSONSchema["schema/outer_array.json"]
inner_object: JSONSchema["schema/outer_array.json", "#"] = {"a_string": "string"}

array = [inner_object]

if TYPE_CHECKING:
    reveal_type(array)
    reveal_type(inner_object)
