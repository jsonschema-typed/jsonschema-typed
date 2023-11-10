import logging
from typing import Union, Any

from mypy.plugin import Plugin, AnalyzeTypeContext
from mypy.types import TypedDictType
import warnings

# Raise issues here.
ISSUE_URL = "https://github.com/jsonschema-typed/jsonschema-typed"


class OptionalTypedDictPlugin(Plugin):

    OptionalTypedDict = "jsonschema_typed.OptionalTypedDict"

    def get_type_analyze_hook(self, fullname: str):
        if fullname == self.OptionalTypedDict:

            def callback(ctx: AnalyzeTypeContext) -> Union[Any, TypedDictType]:
                """Generate annotations from a TypedDict with optional attributes."""
                if not ctx.type.args:
                    return ctx.type

                # First, get the TypedDict analyzed:
                typed_dict_type = ctx.api.analyze_type(ctx.type.args[0])

                # Then remove its required keys. If this doesn't work, the type wasn't a typed dict.
                # If so, we just return back whatever the user gave us.
                try:
                    try:
                        typed_dict_type.required_keys = set()
                    except AttributeError:
                        typed_dict_type.alias.target.required_keys = set()
                except AttributeError:
                    logging.error(
                        "Failed making OptionalTypedDict: Argument in brackets is not a typed dict type.\n"
                        f"Failed at line {ctx.context.line} column {ctx.context.column} (file not known).\n"
                        "The argument in brackets will be used instead."
                    )

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
