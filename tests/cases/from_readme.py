from jsonschema_typed.types import JSONSchema

data: JSONSchema["schema/test-required.json"] = {"title": "some title"}
reveal_type(data)
data["description"] = "there is no description"
data["awesome"] = 42
data["awesome"] = None
