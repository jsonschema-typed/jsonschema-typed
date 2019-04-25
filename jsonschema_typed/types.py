"""Placeholders for supported annotations."""

from typing import Type, Generic, TypeVar
from mypy_extensions import TypedDict


class JSONSchema(dict):
    """Placeholder for JSON schema TypedDict."""


def JSONSchemaBase(schema_path: str) -> Type[dict]:
    """Generate a base class for JSON-schema powered TypedDicts."""
    return dict
