from jsonschema_typed import JSONSchema
from typing import TYPE_CHECKING

data: JSONSchema["schema/nonetype.json"] = {"title": "baz"}
if TYPE_CHECKING:
    reveal_type(data)
data["awesome"] = [1, 2, 3]
data["awesome"] = None
data["awesome"] = 123
