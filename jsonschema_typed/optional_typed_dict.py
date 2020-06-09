from mypy.plugin import Plugin, AnalyzeTypeContext
from mypy.types import TypedDictType
import warnings

# Raise issues here.
ISSUE_URL = "https://github.com/inspera/jsonschema-typed"


class OptionalTypedDictPlugin(Plugin):

    OptionalTypedDict = "jsonschema_typed.OptionalTypedDict"

    def get_type_analyze_hook(self, fullname: str):
        if fullname == self.OptionalTypedDict:

            def callback(ctx: AnalyzeTypeContext) -> TypedDictType:
                """Generate annotations from a TypedDict with optional attributes."""
                if not ctx.type.args:
                    return ctx.type

                # First, get the TypedDict analyzed:
                typed_dict_type = ctx.api.analyze_type(ctx.type.args[0])

                # Then remove its required keys. If this doesn't work, the type wasn't a typed dict.
                # If so, we just return back whatever the user gave us.
                try:
                    typed_dict_type.required_keys = set()
                except AttributeError:
                    pass

                return typed_dict_type

            return callback


def plugin(version: str):
    """See `https://mypy.readthedocs.io/en/latest/extending_mypy.html`_."""
    if float(version) < 0.7:
        warnings.warn(
            "This plugin not tested below mypy 0.710. But you can"
            f" test it and let us know at {ISSUE_URL}."
        )
    return OptionalTypedDictPlugin
