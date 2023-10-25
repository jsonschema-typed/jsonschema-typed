from jsonschema_typed import JSONSchema, OptionalTypedDict
from typing import TYPE_CHECKING

Hard = JSONSchema["schema/hard.json"]

# The key 'num' is required (among others), so this wouldn't be ok without the Optional wrapper.
data: OptionalTypedDict[Hard] = {}

if TYPE_CHECKING:
    reveal_type(data)

data["description"] = "there is no description"
data["num"] = 42
data["num"] = None
