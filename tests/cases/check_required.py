from jsonschema_typed import JSONSchema
from typing import TYPE_CHECKING

data: JSONSchema["schema/check_required.json"] = {"title": "some title"}
if TYPE_CHECKING:
    reveal_type(data)
data["description"] = "there is no description"
data["awesome"] = 42
data["awesome"] = None
