from jsonschema_typed import JSONSchema, OptionalTypedDict
from typing import TYPE_CHECKING

# The key 'awesome' is required, so this wouldn't be ok without the Optional wrapper.
data: OptionalTypedDict[JSONSchema["schema/check_required.json"]] = {
    "title": "some title"
}
if TYPE_CHECKING:
    reveal_type(data)

data["description"] = "there is no description"
data["awesome"] = 42
data["awesome"] = None
