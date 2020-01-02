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
]


@pytest.mark.parametrize("case_file, expected", cases)
def test_cases(case_file: str, expected: Expect):
    normal_report, error_report, exit_status = api.run(
        [os.path.join(case_directory, case_file)]
    )

    for line in expected["normal"].strip().splitlines():
        assert line.strip() in normal_report

    for line in expected["error"].strip().splitlines():
        assert line.strip() in error_report

    assert exit_status == expected["exit_status"]
