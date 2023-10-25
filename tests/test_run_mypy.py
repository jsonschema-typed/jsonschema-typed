"""
This type of test attempts to run mypy on selected sources and asserts that
the output is consistent. This does not (yet) test sufficient edge cases,
and more testing should be done.

# TODO: Add more test cases.
"""

import os
import pytest
from mypy import api
from typing import List, Tuple, TypedDict


class Expect(TypedDict):
    normal: str
    error: str
    exit_status: int


case_directory = os.path.join(os.path.dirname(__file__), "cases")

cases: List[Tuple[str, Expect]] = [
    (
        "from_readme.py",
        Expect(
            normal="""
                note: Revealed type is 'TypedDict('FooSchema', {'title'?: builtins.str, 'awesome'?: builtins.int})'
                error: TypedDict "FooSchema" has no key 'description'
                error: Argument 2 has incompatible type "None"; expected "int"
            """,
            error="",
            exit_status=1,
        ),
    ),
    (
        "check_required.py",
        Expect(
            normal="""
                error: Key 'awesome' missing for TypedDict "FooSchema"
                note: Revealed type is 'TypedDict('FooSchema', {'title'?: builtins.str, 'awesome': builtins.int})'
                error: TypedDict "FooSchema" has no key 'description'
                error: Argument 2 has incompatible type "None"; expected "int"
            """,
            error="",
            exit_status=1,
        ),
    ),
    (
        "alias.py",
        Expect(
            normal="""
                note: Revealed type is 'TypedDict('FooSchema', {'title'?: builtins.str, 'awesome'?: builtins.int})'
                error: TypedDict "FooSchema" has no key 'description'
                error: Argument 2 has incompatible type "None"; expected "int"
            """,
            error="",
            exit_status=1,
        ),
    ),
    (
        "nonetype.py",
        Expect(
            normal="""
                note: Revealed type is 'TypedDict('NoneSchema', {'title'?: builtins.str, 'awesome'?: Union[builtins.list[Any], None]})'
                error: Argument 2 has incompatible type "int"; expected "Optional[List[Any]]"
            """,
            error="",
            exit_status=1,
        ),
    ),
    (
        "nested.py",
        Expect(
            normal="""
                note: Revealed type is 'TypedDict('NestedFooSchema', {'title': builtins.str, 'awesome'?: TypedDict({'nested'?: TypedDict({'thing': builtins.str}), 'thing': builtins.int})})'
                note: Revealed type is 'TypedDict('NestedFooSchemaAwesome', {'nested'?: TypedDict({'thing': builtins.str}), 'thing': builtins.int})'
                note: Revealed type is 'TypedDict('NestedFooSchemaAwesomeNested', {'thing': builtins.str})'
            """,
            error="",
            exit_status=1,
        ),
    ),
    (
        "hard.py",
        Expect(
            normal="""
                note: Revealed type is 'TypedDict('ComplicatedJson', {'num': builtins.int, 'status': builtins.list[TypedDict({'code'?: Union[Literal['success'], Literal['failure']], 'diagnostics'?: builtins.list[TypedDict({'field'?: builtins.str, 'illegal_value'?: builtins.str, 'level': Union[Literal['info'], Literal['warn'], Literal['error']], 'mismatch_fields'?: builtins.list[builtins.str], 'ids'?: builtins.list[TypedDict({'id': builtins.int, 'thing_type'?: Union[Literal['A'], Literal['B']]})]})], 'message'?: builtins.str, 'module': Union[Literal['m1'], Literal['m2']]})]})'
                note: Revealed type is 'builtins.int'
                note: Revealed type is 'builtins.list[TypedDict({'code'?: Union[Literal['success'], Literal['failure']], 'diagnostics'?: builtins.list[TypedDict({'field'?: builtins.str, 'illegal_value'?: builtins.str, 'level': Union[Literal['info'], Literal['warn'], Literal['error']], 'mismatch_fields'?: builtins.list[builtins.str], 'ids'?: builtins.list[TypedDict({'id': builtins.int, 'thing_type'?: Union[Literal['A'], Literal['B']]})]})], 'message'?: builtins.str, 'module': Union[Literal['m1'], Literal['m2']]})]'
                note: Revealed type is 'TypedDict({'code'?: Union[Literal['success'], Literal['failure']], 'diagnostics'?: builtins.list[TypedDict({'field'?: builtins.str, 'illegal_value'?: builtins.str, 'level': Union[Literal['info'], Literal['warn'], Literal['error']], 'mismatch_fields'?: builtins.list[builtins.str], 'ids'?: builtins.list[TypedDict({'id': builtins.int, 'thing_type'?: Union[Literal['A'], Literal['B']]})]})], 'message'?: builtins.str, 'module': Union[Literal['m1'], Literal['m2']]})'
                note: Revealed type is 'builtins.list[TypedDict({'field'?: builtins.str, 'illegal_value'?: builtins.str, 'level': Union[Literal['info'], Literal['warn'], Literal['error']], 'mismatch_fields'?: builtins.list[builtins.str], 'ids'?: builtins.list[TypedDict({'id': builtins.int, 'thing_type'?: Union[Literal['A'], Literal['B']]})]})]'
                note: Revealed type is 'TypedDict({'field'?: builtins.str, 'illegal_value'?: builtins.str, 'level': Union[Literal['info'], Literal['warn'], Literal['error']], 'mismatch_fields'?: builtins.list[builtins.str], 'ids'?: builtins.list[TypedDict({'id': builtins.int, 'thing_type'?: Union[Literal['A'], Literal['B']]})]})'
                note: Revealed type is 'TypedDict('ComplicatedJsonStatusDiagnostics', {'field'?: builtins.str, 'illegal_value'?: builtins.str, 'level': Union[Literal['info'], Literal['warn'], Literal['error']], 'mismatch_fields'?: builtins.list[builtins.str], 'ids'?: builtins.list[TypedDict({'id': builtins.int, 'thing_type'?: Union[Literal['A'], Literal['B']]})]})'
            """,
            error="",
            exit_status=1,
        ),
    ),
    (
        "optional_typed_dict.py",
        Expect(
            normal="""
                note: Revealed type is 'TypedDict('FooSchema', {'title'?: builtins.str, 'awesome'?: builtins.int})'
                error: TypedDict "FooSchema" has no key 'description'
                error: Argument 2 has incompatible type "None"; expected "int"
            """,
            error="",
            exit_status=1,
        ),
    ),
    (
        "optional_typed_dict_hard_mode.py",
        Expect(
            normal="""
                note: Revealed type is 'TypedDict('ComplicatedJson', {'num'?: builtins.int, 'status'?: builtins.list[TypedDict({'code'?: Union[Literal['success'], Literal['failure']], 'diagnostics'?: builtins.list[TypedDict({'field'?: builtins.str, 'illegal_value'?: builtins.str, 'level': Union[Literal['info'], Literal['warn'], Literal['error']], 'mismatch_fields'?: builtins.list[builtins.str], 'ids'?: builtins.list[TypedDict({'id': builtins.int, 'thing_type'?: Union[Literal['A'], Literal['B']]})]})], 'message'?: builtins.str, 'module': Union[Literal['m1'], Literal['m2']]})]})'
                error: TypedDict "ComplicatedJson" has no key 'description'
                error: Argument 2 has incompatible type "None"; expected "int"
            """,
            error="",
            exit_status=1,
        ),
    ),
    (
        "outer_array.py",
        Expect(
            normal="""
            note: Revealed type is 'builtins.list[TypedDict({'a_number'?: builtins.int, 'a_string': builtins.str, 'nested_array_of_numbers'?: builtins.list[builtins.list[builtins.float]]})]'
            note: Revealed type is 'TypedDict('ArrayOfObjects', {'a_number'?: builtins.int, 'a_string': builtins.str, 'nested_array_of_numbers'?: builtins.list[builtins.list[Union[builtins.int, builtins.float]]]})'
            """,
            error="",
            exit_status=1,
        ),
    ),
    (
        "tuple.py",
        Expect(
            normal="""
            tests/cases/tuple.py:9: error: List item 0 has incompatible type "List[str]"; expected "Optional[Tuple[Optional[str], Optional[str]]]"
            tests/cases/tuple.py:10: error: List item 0 has incompatible type "Tuple[str, str, str]"; expected "Optional[Tuple[Optional[str], Optional[str]]]"
            tests/cases/tuple.py:11: error: List item 0 has incompatible type "int"; expected "Optional[Tuple[Optional[str], Optional[str]]]"
            tests/cases/tuple.py:12: error: List item 0 has incompatible type "Tuple[int, int]"; expected "Optional[Tuple[Optional[str], Optional[str]]]"
            tests/cases/tuple.py:15: note: Revealed type is 'builtins.list[Union[Tuple[Union[builtins.str, None], Union[builtins.str, None]], None]]'
            Found 4 errors in 1 file (checked 1 source file)
            """,
            error="",
            exit_status=1,
        ),
    ),
]


@pytest.mark.parametrize("case_file, expected", cases)
def test_cases(case_file: str, expected: Expect):
    normal_report, error_report, exit_status = api.run(
        ["--show-traceback", os.path.join(case_directory, case_file)]
    )

    for line in expected["normal"].strip().splitlines():
        assert line.strip() in normal_report

    for line in expected["error"].strip().splitlines():
        assert line.strip() in error_report

    assert exit_status == expected["exit_status"]
