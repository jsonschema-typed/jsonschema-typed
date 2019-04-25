"""Provides :class:`.JSONSchemaPlugin`."""

import os
import warnings
from mypy.plugin import Plugin, AnalyzeTypeContext, DynamicClassDefContext
import json
from typing import Optional, Callable, Any, Union, List, Set, Dict
import copy

from collections import OrderedDict
from mypy.types import TypedDictType, Instance, UnionType, LiteralType, \
    PartialType, AnyType, TypeOfAny, NoneTyp, UnboundType, ForwardRef, Type
from mypy.nodes import TypeInfo, ClassDef, Block, SymbolTable, Var, \
    SymbolTableNode, GDEF
from mypy import semanal_typeddict
import mypy_extensions
from jsonschema.validators import validator_for
from jsonschema import RefResolver
from jsonschema.validators import _id_of as id_of

ISSUE_URL = 'https://github.com/erickpeirson/jsonschema-typed'
"""Raise issues here."""


# Monkey-patching `warnings.formatwarning`.
def formatwarning(message, category, filepath, lineno, line=None):
    """Make the warnings a bit prettier."""
    _, filename = os.path.split(filepath)
    return f'{filename}:{lineno} {category.__name__}: {message}\n'


warnings.formatwarning = formatwarning


class API:
    """Base class for JSON schema types API."""

    NO_VALUE = 'the buffalo from buffalo who are buffaloed by the buffalo'
    """Needed something other than `None`, so why not."""

    def __init__(self, resolver: RefResolver, outer_name: str) -> None:
        """Initialize with a resolver."""
        self.resolver = resolver
        self.outer_name = outer_name

    def get_type_handler(self, schema_type: str) -> Callable:
        """Get a handler from this schema draft version."""
        if schema_type.startswith('_'):
            raise AttributeError('No way friend')
        handler = getattr(self, schema_type, None)
        if handler is None:
            raise NotImplementedError(f'Type `{schema_type}` is not supported.'
                                      ' If you think that this is an error,'
                                      f' say something at {ISSUE_URL}')
        return handler

    def get_type(self, ctx: AnalyzeTypeContext, schema: Dict[str, Any],
                 outer=False) -> Type:
        """Get a :class:`.Type` for a JSON schema."""
        scope = id_of(schema)
        if scope:
            self.resolver.push_scope(scope)

        # 6.1.1. type
        # The value of this keyword MUST be either a string or an array. If it
        # is an array, elements of the array MUST be strings and MUST be
        # unique.
        #
        # String values MUST be one of the six primitive types ("null",
        # "boolean", "object", "array", "number", or "string"), or "integer"
        # which matches any number with a zero fractional part.
        #
        # An instance validates if and only if the instance is in any of the
        # sets listed for this keyword.
        schema_type = schema.get('type')
        if type(schema_type) is list:
            if outer:
                # Cases in which the root of the schema is anything other than
                # an object are not terribly interesting for this project, so
                # we'll ignore them for now.
                if 'object' not in schema_type:
                    raise NotImplementedError(
                        'Schemas with a root type other than ``object`` are'
                        ' not currently supported.'
                    )
                warnings.warn(f'Root type is an array, which is out of scope'
                              ' for this library. Falling back to `object`. If'
                              ' you believe this to be in error, say so at'
                              f' {ISSUE_URL}')
                schema_type = 'object'
            else:
                return UnionType([
                    self._get_type(ctx, schema, primitive_type, outer=outer)
                    for primitive_type in schema_type
                ])
        elif schema_type is None:
            if '$ref' in schema:
                return self.ref(ctx, schema['$ref'])
            elif 'allOf' in schema:
                return self.allOf(ctx, schema['allOf'])
            elif 'anyOf' in schema:
                return self.anyOf(ctx, schema['anyOf'])
            elif 'enum' in schema:
                return self.enum(ctx, schema['enum'])
            elif 'default' in schema:
                return self.default(ctx, schema['default'])
        if scope:
            self.resolver.pop_scope()

        if outer and schema_type != 'object':
            raise NotImplementedError(
                'Schemas with a root type other than ``object`` are not'
                ' currently supported.'
            )
        return self._get_type(ctx, schema, schema_type, outer=outer)

    def _get_type(self, ctx: AnalyzeTypeContext, schema: Dict[str, Any],
                  schema_type: str, outer=False) -> Type:
        handler = self.get_type_handler(schema_type)
        if handler is not None:
            return handler(ctx, schema, outer=outer)

        warnings.warn(f'No handler for `{schema_type}`; please raise an issue'
                      f' at {ISSUE_URL} if you believe this to be in error')
        return AnyType(TypeOfAny.unannotated)


class APIv4(API):
    """JSON Schema draft 4."""

    def const(self, ctx: AnalyzeTypeContext, const: Union[int, str, bool],
              **kwargs) -> LiteralType:
        """Generate a ``Literal`` for a const value."""
        name = type(const).__name__
        return LiteralType(const, named_builtin_type(ctx, name, []))

    def enum(self, ctx: AnalyzeTypeContext, values: List[Union[str, int]],
             **kwargs) -> UnionType:
        """Generate a ``Union`` of ``Literal``s for an enum."""
        return UnionType([self.const(ctx, value) for value in values])

    def boolean(self, ctx: AnalyzeTypeContext, schema, **kwargs):
        """Generate a ``bool`` annotation for a boolean object."""
        if 'properties' in schema:
            default = schema['properties'].get('default', self.NO_VALUE)
            if default != self.NO_VALUE:
                warnings.warn('`default` keyword not supported; but see: '
                              'https://github.com/python/mypy/issues/6131')
            const = schema['properties'].get('const', self.NO_VALUE)
            if const != self.NO_VALUE:
                return self.const(ctx, const)
        return named_builtin_type(ctx, 'bool', [])

    def object(self, ctx: AnalyzeTypeContext, schema: Dict[str, Any],
               outer: bool = False, **kwargs) -> Type:
        """Generate an annotation for an object, usually a TypedDict."""
        properties = schema.get('properties')

        if properties is None:
            return named_builtin_type(ctx, 'dict')

        try:
            fallback = ctx.api.named_type('mypy_extensions._TypedDict', [])
        except AssertionError:
            fallback = named_builtin_type(ctx, 'dict', [])
        items, types = zip(*filter(lambda o: o[1] is not None, [
            (prop, self.get_type(ctx, subschema))
            for prop, subschema in properties.items()
            if prop not in ['default', 'const']     # These are reserved names,
                                                    # not properties.
        ]))
        required_keys = set(schema.get('required', []))

        if outer:
            # We want to name the outer Type, so that we can support nested
            # references. Note that this may not be fully supported in mypy
            # at this time.
            info = self._build_typeddict_typeinfo(ctx, self.outer_name,
                                                  list(items), list(types),
                                                  required_keys)
            instance = Instance(info, [])
            td = info.typeddict_type
            typing_type = td.copy_modified(item_types=list(td.items.values()),
                                           fallback=instance)
            # # Resolve any forward (nested) references to this Type.
            # if self.forward_refs:
            #
            # for fw in self.forward_refs:
            #     fw.resolve(typing_type)
            return typing_type

        struct = OrderedDict(zip(items, types))
        return TypedDictType(struct, required_keys, fallback)

    def array(self, ctx: AnalyzeTypeContext,
              schema: Optional[Union[bool, dict]], **kwargs) -> Type:
        """Generate a ``List[]`` annotation with the allowed types."""
        items = schema.get('items')
        if items is True:
            inner_types = [AnyType(TypeOfAny.unannotated)]
        elif items is False:
            raise NotImplementedError('"items": false is not supported')
        elif items is not None:
            inner_types = [self.get_type(ctx, items)]
        else:
            inner_types = []
        return named_builtin_type(ctx, 'list', inner_types)

    def allOf(self, ctx: AnalyzeTypeContext, subschema: List[dict], **kwargs):
        """
        Generate a ``Union`` annotation with the allowed types.

        Unfortunately PEP 544 currently does not support an Intersection type;
        see `this issue <https://github.com/python/typing/issues/213>`_ for
        some context.
        """
        warnings.warn('PEP 544 does not support an Intersection type, so '
                      ' `allOf` is interpreted as a `Union` for now; see'
                      ' https://github.com/python/typing/issues/213')
        return UnionType(list(filter(lambda o: o is not None,
                                     [self.get_type(ctx, subs)
                                      for subs in subschema])))

    def anyOf(self, ctx: AnalyzeTypeContext, subschema: List, **kwargs):
        """Generate a ``Union`` annotation with the allowed types."""
        return UnionType(list(filter(lambda o: o is not None,
                                     [self.get_type(ctx, subs)
                                      for subs in subschema])))

    def any(self, ctx: AnalyzeTypeContext, subschema, **kwargs):
        """Generate an ``Any`` annotation."""
        return AnyType(TypeOfAny.unannotated)

    def ref(self, ctx: AnalyzeTypeContext, ref: str, **kwargs):
        """Handle a `$ref`."""
        if ref == '#':      # Self ref.
            # Per @ilevkivskyi:
            #
            # > You should never use ForwardRef manually
            # > Also it is deprecated and will be removed soon
            # > Support for recursive types is limited to proper classes
            # > currently
            #
            # forward_ref = ForwardRef(UnboundType(self.outer_name))
            # self.forward_refs.append(forward_ref)
            # return forward_ref
            warnings.warn('Forward references may not be supported; see'
                          ' https://github.com/python/mypy/issues/731')
            return self.object(ctx, {})
        resolve = getattr(self.resolver, "resolve", None)
        if resolve is None:
            with self.resolver.resolving(ref) as resolved:
                return self.get_type(ctx, resolved)
        else:
            scope, resolved = self.resolver.resolve(ref)
            self.resolver.push_scope(scope)
            try:
                return self.get_type(ctx, resolved)
            finally:
                self.resolver.pop_scope()

    def string(self, ctx: AnalyzeTypeContext, *args, **kwargs):
        """Generate a ``str`` annotation."""
        return named_builtin_type(ctx, 'str')

    def number(self, ctx: AnalyzeTypeContext, *args, **kwargs):
        """Generate a ``Union[int, float]`` annotation."""
        return UnionType([named_builtin_type(ctx, 'int'),
                          named_builtin_type(ctx, 'float')])

    def integer(self, ctx: AnalyzeTypeContext, *args, **kwargs):
        """Generate an ``int`` annotation."""
        return named_builtin_type(ctx, 'int')

    def default(self, ctx: AnalyzeTypeContext, *args, **kwargs) -> None:
        """
        The ``default`` keyword is not supported.

        But see: `https://github.com/python/mypy/issues/6131`_.
        """
        warnings.warn('`default` keyword not supported; but see: '
                      'https://github.com/python/mypy/issues/6131')
        return None

    def _basic_new_typeinfo(self, ctx: AnalyzeTypeContext, name: str,
                            basetype_or_fallback: Instance) -> TypeInfo:
        """
        Build a basic :class:`.TypeInfo`.

        This was basically lifted from ``mypy.semanal``.
        """
        class_def = ClassDef(name, Block([]))
        class_def.fullname = name

        info = TypeInfo(SymbolTable(), class_def, '')
        class_def.info = info
        mro = basetype_or_fallback.type.mro
        if not mro:
            mro = [basetype_or_fallback.type,
                   named_builtin_type(ctx, 'object').type]
        info.mro = [info] + mro
        info.bases = [basetype_or_fallback]
        return info

    def _build_typeddict_typeinfo(self, ctx: AnalyzeTypeContext, name: str,
                                  items: List[str], types: List[Type],
                                  required_keys: Set[str]) -> TypeInfo:
        """
        Build a :class:`.TypeInfo` for a TypedDict.

        This was basically lifted from ``mypy.semanal_typeddict``.
        """
        try:
            fallback = ctx.api.named_type('mypy_extensions._TypedDict', [])
        except AssertionError:
            fallback = named_builtin_type(ctx, 'dict')
        info = self._basic_new_typeinfo(ctx, name, fallback)
        info.typeddict_type = TypedDictType(OrderedDict(zip(items, types)),
                                            required_keys, fallback)
        return info


class APIv6(APIv4):
    """JSON Schema draft 6."""

    def integer(self, ctx: AnalyzeTypeContext, *args, **kwargs) -> UnionType:
        """Generate a ``Union`` annotation for an integer."""
        return UnionType([named_builtin_type(ctx, 'int'),
                          named_builtin_type(ctx, 'float')])


class APIv7(APIv6):
    """JSON Schema draft 7."""


class JSONSchemaPlugin(Plugin):
    """Provides support for the JSON Schema as TypedDict."""

    JSONSchema = 'jsonschema_typed.types.JSONSchema'
    JSONSchemaBase = 'jsonschema_typed.types.JSONSchemaBase'

    def get_type_analyze_hook(self, fullname: str) -> Optional[Callable]:
        """Produce an analyzer callback if a JSONSchema annotation is found."""
        if fullname == self.JSONSchema:
            def callback(ctx: AnalyzeTypeContext) -> TypedDictType:
                """Generate annotations from a JSON Schema."""
                if not ctx.type.args:
                    return ctx.type
                schema_path, = ctx.type.args
                schema_path = os.path.abspath(schema_path.literal_value)
                schema = self._load_schema(schema_path)
                make_type = TypeMaker(schema_path, schema)
                _type = make_type(ctx)
                return _type
            return callback

    def get_dynamic_class_hook(self, fullname: str) -> Optional[Callable]:
        """Add support for ``JSONSchemaBase``."""
        if fullname == self.JSONSchemaBase:
            return self.dyn_class_hook
        return None

    def _load_schema(self, path: str) -> dict:
        with open(path) as f:
            return json.load(f)

    def get_additional_deps(self, file):
        """Add ``mypy_extensions`` as a dependency."""
        return [(10, 'mypy_extensions', -1)]

    def dyn_class_hook(self, ctx: DynamicClassDefContext) -> TypedDictType:
        """Generate annotations from a JSON Schema."""
        schema_path, = ctx.call.args
        schema_path = os.path.abspath(schema_path.value)
        schema = self._load_schema(schema_path)
        make_type = TypeMaker(schema_path, schema)
        td_type = make_type(ctx)

        class_def = ClassDef(ctx.name, Block([]))
        class_def.fullname = ctx.api.qualified_name(ctx.name)
        info = TypeInfo(SymbolTable(), class_def, ctx.api.cur_mod_id)
        info.typeddict_type = td_type

        dict_type = named_builtin_type(ctx, 'dict')
        mro = dict_type.type.mro
        if not mro:
            mro = [dict_type.type, named_builtin_type(ctx, 'object').type]

        class_def.info = info
        info.mro = mro
        info.bases = [dict_type]
        ctx.api.add_symbol_table_node(ctx.name, SymbolTableNode(GDEF, info))


class TypeMaker:
    r"""Makes :class:`.Type`\s from a JSON schema."""

    def __init__(self, schema_path: str, schema: Dict[str, Any],
                 api_version: type = APIv7) -> None:
        """Set up a resolver and API instance."""
        self.schema = schema
        self.outer_name = self._sanitize_name(
            self.schema.get('title', 'JSONSchema'))
        self.schema_path = schema_path
        self.resolver = RefResolver.from_schema(schema, id_of=id_of)
        self.forward_refs = []
        self.api = api_version(self.resolver, self.outer_name)

    def _sanitize_name(self, name: str) -> str:
        return name.replace('-', ' ').title().replace(' ', '')

    def __call__(self, ctx: AnalyzeTypeContext) -> Type:
        """Generate the appropriate types for this schema."""
        return self.api.get_type(ctx, self.schema, outer=True)


def plugin(version: str):
    """See `https://mypy.readthedocs.io/en/latest/extending_mypy.html`_."""
    if float(version) < 0.7:
        warnings.warn('This plugin not tested below mypy 0.710. But you can'
                      f' test it and let us know at {ISSUE_URL}.')
    return JSONSchemaPlugin


def named_builtin_type(ctx: Union[AnalyzeTypeContext, DynamicClassDefContext],
                       name: str, *args, **kwargs) -> Type:
    """
    For some reason (probably a good one) these APIs expect different names.
    """
    if type(ctx) is AnalyzeTypeContext:
        mod = 'builtins'
    elif type(ctx) is DynamicClassDefContext:
        mod = '__builtins__'
    return ctx.api.named_type(f'{mod}.{name}', *args, **kwargs)
