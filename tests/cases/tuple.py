from jsonschema_typed import JSONSchema
from typing import TYPE_CHECKING


Ty = JSONSchema["schema/tuple.json"]

data: Ty = [("key", "value")]

error0: Ty = [["key", "value"]]
error1: Ty = [("key", "value", "toomuch")]
error2: Ty = [1]
error3: Ty = [(1, 2)]

if TYPE_CHECKING:
    reveal_type(data)
