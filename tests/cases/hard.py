from jsonschema_typed import JSONSchema
from typing import TYPE_CHECKING, Final, Literal, TypedDict, Type


data: JSONSchema["schema/hard.json"]
number: JSONSchema["schema/hard.json", "num"]
status: JSONSchema["schema/hard.json", "status"]
diagnostics_list: JSONSchema["schema/hard.json", "status", "diagnostics"]
diagnostics: JSONSchema["schema/hard.json", "status", "diagnostics", "#"]

diagnostics_list = [{"level": "warn"}]
if TYPE_CHECKING:
    reveal_type(data)
    reveal_type(number)
    reveal_type(status)
    reveal_type(status[0])
    reveal_type(diagnostics_list)
    reveal_type(diagnostics_list[0])
    reveal_type(diagnostics)
